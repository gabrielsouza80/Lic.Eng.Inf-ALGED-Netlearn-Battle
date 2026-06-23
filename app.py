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


def login_required(view):
    """Protege páginas que exigem login."""
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


@app.route("/play", methods=["GET", "POST"])
@login_required
def play():
    if request.method == "POST":
        try:
            level = int(request.form.get("level", ""))
        except ValueError:
            level = 0
        question = game.create_question(level)
        if question is None:
            flash("Não existem perguntas para este nível.", "error")
            return redirect(url_for("play"))
        # Guardamos a pergunta atual na sessão até o aluno enviar a resposta.
        session["question"] = question
        session["started_at"] = time.time()
        return render_template("play.html", question=question, level_name=LEVELS[level])
    return render_template("play.html", levels=LEVELS)


@app.route("/answer", methods=["POST"])
@login_required
def answer():
    question = session.pop("question", None)
    started_at = session.pop("started_at", time.time())
    if question is None:
        flash("Escolha um nível antes de responder.", "error")
        return redirect(url_for("play"))
    try:
        selected_index = int(request.form.get("choice", "-1"))
    except ValueError:
        selected_index = -1
    result = game.save_attempt(session["username"], question, selected_index, started_at)
    return render_template("result.html", result=result, level=question["level"], question=question["question"])


@app.route("/history")
@login_required
def history():
    attempts = list(reversed(game.history_for(session["username"])[-20:]))
    return render_template("history.html", attempts=attempts)


@app.route("/stats")
@login_required
def statistics():
    username = session["username"]
    return render_template("stats.html", stats=stats.personal_statistics(username),
                           score=scores.get_score(username))


@app.route("/ranking")
def ranking():
    return render_template("ranking.html", ranking=scores.top_five())


@app.route("/teacher")
def teacher():
    # Área pública e simples para demonstração; não existe login de professor.
    return render_template("teacher.html", ranking=scores.top_five(),
                           stats=stats.global_statistics(),
                           attempts=game.recent_attempts())


@app.route("/rules")
def rules():
    return render_template("rules.html")


if __name__ == "__main__":
    app.run(debug=os.environ.get("FLASK_DEBUG") == "1")
