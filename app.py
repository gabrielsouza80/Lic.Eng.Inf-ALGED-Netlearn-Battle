"""[Secções 1, 4 e 5] Interface web Flask e rotas do NetLearn Battle."""
import os
import secrets
import time
from functools import wraps

from flask import Flask, flash, redirect, render_template, request, session, url_for

from services.auth_service import AuthService
from services.game_service import GameService
from services.json_service import load
from services.score_service import ScoreService
from services.stats_service import StatsService

app = Flask(__name__)
# [Secção 12] A chave assina os dados da sessão do utilizador.
app.config["SECRET_KEY"] = os.environ.get("FLASK_SECRET_KEY") or secrets.token_hex(32)

auth = AuthService()
game = GameService()
scores = ScoreService()
stats = StatsService()

LEVELS = {
    1: "IPv4 básico",
    2: "Sub-redes IPv4",
    3: "Super-redes IPv4",
    4: "IPv6 simples",
    5: "ACLs simples",
}


def login_required(view):
    """[Secção 13] Protege páginas que exigem login."""
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "username" not in session:
            flash("Faça login para continuar.", "error")
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    # [Secções 8, 9 e 10] Recebe o formulário e chama o serviço de registo.
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        ok, message = auth.register(username, password)
        flash(message, "success" if ok else "error")
        return redirect(url_for("login") if ok else url_for("register"))
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    # [Secções 11 e 12] Confirma o login e guarda o username na sessão.
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        if auth.login(username, password):
            session.clear()
            session["username"] = username
            return redirect(url_for("dashboard"))
        flash("Utilizador ou password incorretos.", "error")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


@app.route("/dashboard")
@login_required
def dashboard():
    username = session["username"]
    return render_template("dashboard.html", username=username, score=scores.get_score(username))


@app.route("/play", methods=["GET", "POST"])
@login_required
def play():
    # [Secção 14] Mostra níveis ou guarda a pergunta atual na sessão.
    if request.method == "POST":
        try:
            level = int(request.form.get("level", ""))
        except ValueError:
            level = 0
        questions = game.create_session_questions(level)
        if not questions:
            flash("Não existem perguntas para este nível.", "error")
            return redirect(url_for("play"))
        question = questions.pop(0)
        # Guardamos a pergunta atual na sessão até o aluno enviar a resposta.
        session["question"] = question
        session["question_queue"] = questions
        session["game_session_id"] = secrets.token_hex(6)
        session["session_summary"] = {"total": 0, "correct": 0, "wrong": 0, "points": 0}
        session["started_at"] = time.time()
        # get dá um nome seguro mesmo se uma pergunta JSON tiver um nível novo.
        return render_template("play.html", question=question,
                               level_name=LEVELS.get(level, f"Nível {level}"))
    return render_template("play.html", levels=LEVELS)


@app.route("/next")
@login_required
def next_question():
    """Retira a próxima pergunta da fila criada para a sessão atual."""
    questions = session.get("question_queue", [])
    if not questions:
        flash("A fila deste nível terminou. Escolha outro nível.", "success")
        return redirect(url_for("play"))
    session["question"] = questions.pop(0)
    session["question_queue"] = questions
    session["started_at"] = time.time()
    question = session["question"]
    return render_template("play.html", question=question,
                           level_name=LEVELS.get(question["level"], "Nível"))


@app.route("/training")
@login_required
def training():
    """Cria uma Queue com perguntas que o aluno errou em tentativas anteriores."""
    errors = [item for item in game.history_for(session["username"])
              if not item.get("is_correct") and isinstance(item.get("options"), list)]
    if not errors:
        flash("Ainda não existem perguntas erradas disponíveis para treino.", "success")
        return redirect(url_for("dashboard"))
    questions = []
    for attempt in reversed(errors[-5:]):
        options = attempt["options"]
        questions.append({"level": attempt["level"], "topic": attempt["topic"],
                          "question": attempt["question"], "options": options,
                          "correct_index": options.index(attempt["correct_answer"]),
                          "points_correct": 0, "points_wrong": 0,
                          "question_type": "training"})
    question = questions.pop(0)
    session["question"] = question
    session["question_queue"] = questions
    session["started_at"] = time.time()
    return render_template("play.html", question=question, level_name="Modo treino")


@app.route("/answer", methods=["POST"])
@login_required
def answer():
    # [Secções 14 e 27] Corrige a resposta, guarda tentativa e atualiza score.
    question = session.pop("question", None)
    started_at = session.pop("started_at", time.time())
    if question is None:
        flash("Escolha um nível antes de responder.", "error")
        return redirect(url_for("play"))
    try:
        selected_index = int(request.form.get("choice", "-1"))
    except ValueError:
        selected_index = -1
    try:
        result = game.save_attempt(session["username"], question, selected_index, started_at,
                                   session.get("game_session_id"))
    except ValueError as error:
        # Se um ficheiro JSON tiver sido alterado para um formato inválido, a
        # aplicação informa o problema em vez de apresentar uma página de erro.
        flash(str(error), "error")
        return redirect(url_for("play"))
    summary = session.get("session_summary", {"total": 0, "correct": 0, "wrong": 0, "points": 0})
    summary["total"] += 1
    summary["correct" if result["is_correct"] else "wrong"] += 1
    summary["points"] += result["points"]
    session["session_summary"] = summary
    finished = not session.get("question_queue")
    return render_template("result.html", result=result, level=question["level"], question=question["question"],
                           summary=summary, finished=finished)


@app.route("/history")
@login_required
def history():
    # [Secção 29] Mostra tentativas anteriores do aluno autenticado.
    attempts = list(reversed(game.history_for(session["username"])[-20:]))
    return render_template("history.html", attempts=attempts)


@app.route("/stats")
@login_required
def statistics():
    # [Secções 30 a 33] Mostra estatísticas calculadas a partir das tentativas.
    username = session["username"]
    return render_template("stats.html", stats=stats.personal_statistics(username),
                           score=scores.get_score(username), evolution=stats.score_evolution(username))


@app.route("/ranking")
def ranking():
    # [Secção 28] Mostra o Top 5 baseado em scores.json.
    return render_template("ranking.html", ranking=scores.top_five())


@app.route("/teacher", methods=["GET", "POST"])
def teacher():
    # [Secção 34] Área pública e simples para consultar dados globais.
    all_attempts = game.recent_attempts(limit=10000)
    tcp_command = None
    if request.method == "POST":
        host = request.form.get("host", "127.0.0.1").strip() or "127.0.0.1"
        try:
            port = int(request.form.get("port", 5001))
            level = int(request.form.get("level", 1))
            amount = int(request.form.get("questions", 5))
        except ValueError:
            port, level, amount = 5001, 1, 5
        tcp_command = f"py -3 network/server.py --host {host} --port {port} --level {level} --questions {amount}"
    return render_template("teacher.html", ranking=scores.top_five(),
                           stats=stats.global_statistics(), attempts=game.recent_attempts(),
                           quartiles=stats.score_quartiles(load("scores.json", {})),
                           accuracy_by_type=stats.accuracy_by_type(all_attempts), tcp_command=tcp_command)


@app.route("/rules")
def rules():
    return render_template("rules.html")


if __name__ == "__main__":
    # A porta 5000 é usada normalmente. Os testes Robot usam 5002.
    port = int(os.environ.get("FLASK_PORT", "5000"))
    app.run(port=port, debug=os.environ.get("FLASK_DEBUG") == "1")
