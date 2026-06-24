"""Interface web Flask do NetLearn Battle."""
import os
import secrets
import time
from functools import wraps

from flask import Flask, flash, redirect, render_template, request, session, url_for

from services.auth_service import AuthService
from services.game_service import GameService
from services.score_service import ScoreService
from services.stats_service import StatsService

app = Flask(__name__)
# A chave assina os dados da sessão. Em produção deve ser definida no sistema.
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

# Chaves usadas na sessão Flask para guardar o estado da sessão de jogo.
GAME_KEYS = ("session_id", "session_level", "session_queue", "current_question",
             "session_attempts", "session_stats", "started_at")


def login_required(view):
    """Protege páginas que exigem login."""
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "username" not in session:
            flash("Faça login para continuar.", "error")
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped


def _clear_game_session():
    """Limpa o estado da sessão de jogo guardado na sessão Flask."""
    for key in GAME_KEYS:
        session.pop(key, None)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        ok, message = auth.register(username, password)
        flash(message, "success" if ok else "error")
        return redirect(url_for("login") if ok else url_for("register"))
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
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


def _render_current_question():
    """Mostra a pergunta atual da sessão de jogo com o progresso."""
    stats_data = session["session_stats"]
    position = stats_data["answered"] + 1
    return render_template("play.html", question=session["current_question"],
                           level_name=LEVELS[session["session_level"]],
                           position=position, total=stats_data["total"])


@app.route("/play", methods=["GET", "POST"])
@login_required
def play():
    if request.method == "POST":
        try:
            level = int(request.form.get("level", ""))
        except ValueError:
            level = 0
        if level not in LEVELS:
            flash("Nível inválido.", "error")
            return redirect(url_for("play"))
        questions = game.build_session_questions(level)
        if not questions:
            flash("Não existem perguntas para este nível.", "error")
            return redirect(url_for("play"))
        # A Queue da sessão fica guardada como lista (serializável em JSON).
        # FIFO: a primeira pergunta é a primeira a sair.
        session["session_id"] = game.new_session_id()
        session["session_level"] = level
        session["current_question"] = questions[0]
        session["session_queue"] = questions[1:]
        session["session_attempts"] = []
        session["session_stats"] = {"total": len(questions), "answered": 0,
                                    "correct": 0, "wrong": 0, "points": 0}
        session["started_at"] = time.time()
        return _render_current_question()
    # GET: continua uma sessão a decorrer ou mostra a escolha de nível.
    if session.get("current_question"):
        return _render_current_question()
    return render_template("play.html", levels=LEVELS)


@app.route("/answer", methods=["POST"])
@login_required
def answer():
    question = session.get("current_question")
    if question is None:
        flash("Escolha um nível antes de responder.", "error")
        return redirect(url_for("play"))

    try:
        selected_index = int(request.form.get("choice", "-1"))
    except ValueError:
        selected_index = -1

    username = session["username"]
    session_id = session["session_id"]
    level = session["session_level"]
    started_at = session.get("started_at", time.time())

    attempt, result = game.grade_answer(username, question, selected_index,
                                        started_at, session_id)

    attempts = session.get("session_attempts", [])
    attempts.append(attempt)
    session["session_attempts"] = attempts

    stats_data = session["session_stats"]
    stats_data["answered"] += 1
    stats_data["correct" if attempt["is_correct"] else "wrong"] += 1
    stats_data["points"] += attempt["points"]
    session["session_stats"] = stats_data

    queue = session.get("session_queue", [])
    if queue:
        # dequeue(): retira a próxima pergunta da Queue.
        session["current_question"] = queue.pop(0)
        session["session_queue"] = queue
        session["started_at"] = time.time()
        finished = False
    else:
        # Fim da sessão: as tentativas da Stack são gravadas e cria-se o resumo.
        game.save_session_attempts(attempts)
        session["last_summary"] = game.save_session_summary(
            username, session_id, level, attempts)
        _clear_game_session()
        finished = True

    return render_template("result.html", result=result, level=question["level"],
                           question=question["question"], finished=finished,
                           position=stats_data["answered"], total=stats_data["total"])


@app.route("/summary")
@login_required
def summary():
    data = session.get("last_summary")
    if not data:
        return redirect(url_for("play"))
    return render_template("summary.html", summary=data,
                           level_name=LEVELS.get(data["level"], data["level"]),
                           score=scores.get_score(session["username"]))


# ----------------------------------------------------------------------
# Modo treino: repetir perguntas onde o aluno falhou
# ----------------------------------------------------------------------
@app.route("/training")
@login_required
def training():
    questions = game.wrong_questions_for(session["username"])
    if not questions:
        session.pop("training_queue", None)
        session.pop("training_question", None)
        return render_template("training.html", empty=True)
    # As perguntas erradas vão para uma Queue (FIFO) para o aluno repetir.
    session["training_question"] = questions[0]
    session["training_queue"] = questions[1:]
    return render_template("training.html", question=questions[0],
                           remaining=len(questions))


@app.route("/training/answer", methods=["POST"])
@login_required
def training_answer():
    question = session.get("training_question")
    if question is None:
        flash("Não existe pergunta de treino ativa.", "error")
        return redirect(url_for("training"))
    try:
        selected_index = int(request.form.get("choice", "-1"))
    except ValueError:
        selected_index = -1
    result = game.check_training_answer(question, selected_index)
    queue = session.get("training_queue", [])
    next_question = queue.pop(0) if queue else None
    session["training_queue"] = queue
    session["training_question"] = next_question
    return render_template("training.html", result=result,
                           answered_question=question["question"],
                           question=next_question, remaining=len(queue))


@app.route("/history")
@login_required
def history():
    attempts = list(reversed(game.history_for(session["username"])[-20:]))
    return render_template("history.html", attempts=attempts)


@app.route("/stats", endpoint="stats")
@login_required
def statistics():
    username = session["username"]
    return render_template("stats.html", stats=stats.personal_statistics(username),
                           score=scores.get_score(username))


@app.route("/ranking")
def ranking():
    return render_template("ranking.html", ranking=scores.top_five())


@app.route("/teacher", methods=["GET", "POST"])
def teacher():
    # Área pública e simples para demonstração; não existe login de professor.
    tcp_command = None
    if request.method == "POST":
        host = request.form.get("host", "127.0.0.1").strip() or "127.0.0.1"
        port = request.form.get("port", "5001").strip() or "5001"
        level = request.form.get("level", "1").strip() or "1"
        questions = request.form.get("questions", "5").strip() or "5"
        # Apenas geramos o comando; não iniciamos o processo a partir do Flask.
        tcp_command = (f"python network/server.py --host {host} --port {port} "
                       f"--level {level} --questions {questions}")
    return render_template("teacher.html", ranking=scores.top_five(),
                           stats=stats.global_statistics(),
                           quartiles=stats.score_quartiles(),
                           attempts=game.recent_attempts(),
                           levels=LEVELS, tcp_command=tcp_command)


@app.route("/rules")
def rules():
    return render_template("rules.html")


if __name__ == "__main__":
    app.run(debug=os.environ.get("FLASK_DEBUG") == "1")
