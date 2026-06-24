"""Servidor TCP do NetLearn Battle.

Protocolo simples baseado em mensagens JSON (uma por linha). O servidor é a
autoridade: valida sempre as respostas do seu lado e NUNCA envia o índice da
resposta correta dentro da pergunta. Cada cliente tem a sua própria Queue (FIFO)
de perguntas, tal como na versão web.

Tipos de mensagem do cliente -> resposta do servidor:
  AUTH    -> AUTH_RESULT
  START   -> QUESTION | ERROR
  ANSWER  -> ANSWER_RESULT
  NEXT    -> QUESTION | END
  RANKING -> RANKING
  STATS   -> STATS
  (desconhecido / JSON inválido) -> ERROR
"""
import argparse
import json
import os
import socket
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.auth_service import AuthService
from services.game_service import GameService
from services.score_service import ScoreService
from services.stats_service import StatsService
from structures.queue import Queue

# Tempo máximo de inatividade do cliente antes de fechar a ligação.
CLIENT_TIMEOUT_SECONDS = 300


def send_json(connection, message):
    """Envia um objeto Python como uma linha JSON."""
    connection.sendall((json.dumps(message) + "\n").encode("utf-8"))


def public_question(question, position, total):
    """Versão da pergunta para enviar ao cliente, sem o índice correto."""
    return {
        "type": "QUESTION",
        "position": position,
        "total": total,
        "level": question["level"],
        "topic": question["topic"],
        "question": question["question"],
        "options": question["options"],
    }


class ClientSession:
    """Guarda o estado de um cliente ligado (Queue de perguntas e contagem)."""

    def __init__(self, level, count):
        self.game = GameService()
        self.username = None
        self.session_id = self.game.new_session_id()
        self.level = level
        self.count = count
        self.queue = Queue()
        self.current = None
        self.started_at = None
        self.attempts = []
        self.position = 0
        self.total = 0


def handle_auth(state, message):
    success = AuthService().login(message.get("username", ""), message.get("password", ""))
    if success:
        state.username = message.get("username", "")
    return {"type": "AUTH_RESULT", "success": success,
            "message": "Autenticado." if success else "Credenciais inválidas."}


def handle_start(state, message):
    if not state.username:
        return {"type": "ERROR", "message": "Faça AUTH antes de começar."}
    level = int(message.get("level", state.level))
    count = int(message.get("count", state.count))
    questions = state.game.build_session_questions(level, count)
    if not questions:
        return {"type": "ERROR", "message": "Nível sem perguntas."}
    state.level = level
    state.queue = Queue()
    for question in questions:
        state.queue.enqueue(question)
    state.total = len(questions)
    state.position = 1
    state.current = state.queue.dequeue()
    state.started_at = time.time()
    return public_question(state.current, state.position, state.total)


def handle_answer(state, message):
    if state.current is None:
        return {"type": "ERROR", "message": "Não há pergunta ativa."}
    selected_index = message.get("selected_index", -1)
    attempt, result = state.game.grade_answer(
        state.username, state.current, selected_index, state.started_at, state.session_id)
    state.attempts.append(attempt)
    state.current = None
    return {"type": "ANSWER_RESULT", "is_correct": result["is_correct"],
            "correct_answer": result["correct_answer"], "points": result["points"],
            "score": result["score"], "position": state.position, "total": state.total}


def handle_next(state, message):
    if state.queue.is_empty():
        # Fim da sessão: persistir tentativas (Stack) e resumo.
        if state.attempts:
            state.game.save_session_attempts(state.attempts)
            summary = state.game.save_session_summary(
                state.username, state.session_id, state.level, state.attempts)
        else:
            summary = {"total": 0, "correct": 0, "session_points": 0,
                       "final_score": ScoreService().get_score(state.username or "")}
        return {"type": "END", "total": summary["total"], "correct": summary["correct"],
                "session_points": summary["session_points"], "final_score": summary["final_score"]}
    state.position += 1
    state.current = state.queue.dequeue()
    state.started_at = time.time()
    return public_question(state.current, state.position, state.total)


def handle_ranking(state, message):
    return {"type": "RANKING", "ranking": ScoreService().top_five()}


def handle_stats(state, message):
    return {"type": "STATS", "stats": StatsService().global_statistics()}


HANDLERS = {
    "AUTH": handle_auth,
    "START": handle_start,
    "ANSWER": handle_answer,
    "NEXT": handle_next,
    "RANKING": handle_ranking,
    "STATS": handle_stats,
}


def process_message(state, message):
    """Despacha uma mensagem já descodificada para o handler certo."""
    handler = HANDLERS.get(message.get("type"))
    if handler is None:
        return {"type": "ERROR", "message": "Tipo de mensagem desconhecido."}
    return handler(state, message)


def handle_client(connection, address, level, count):
    """Trata um cliente: lê linhas JSON e responde até a ligação fechar."""
    print(f"Cliente ligado: {address}")
    connection.settimeout(CLIENT_TIMEOUT_SECONDS)
    state = ClientSession(level, count)
    reader = connection.makefile("r", encoding="utf-8")
    try:
        for line in reader:
            line = line.strip()
            if not line:
                continue
            try:
                message = json.loads(line)
            except json.JSONDecodeError:
                send_json(connection, {"type": "ERROR", "message": "JSON inválido."})
                continue
            if not isinstance(message, dict):
                send_json(connection, {"type": "ERROR", "message": "Mensagem deve ser um objeto."})
                continue
            response = process_message(state, message)
            send_json(connection, response)
    except socket.timeout:
        print(f"Cliente {address} expirou por inatividade.")
    except (ConnectionError, OSError) as error:
        print(f"Ligação com {address} terminou: {error}")
    finally:
        print(f"Cliente desligado: {address}")


def main():
    parser = argparse.ArgumentParser(description="Servidor TCP do NetLearn Battle.")
    parser.add_argument("--host", default="127.0.0.1", help="Endereço de escuta.")
    parser.add_argument("--port", type=int, default=5001, help="Porta de escuta.")
    parser.add_argument("--level", type=int, default=1, help="Nível por omissão.")
    parser.add_argument("--questions", type=int, default=5, help="Perguntas por sessão.")
    args = parser.parse_args()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((args.host, args.port))
        server.listen()
        print(f"Servidor TCP em {args.host}:{args.port} (nível {args.level}, "
              f"{args.questions} perguntas). Ctrl+C para parar.")
        try:
            while True:
                connection, address = server.accept()
                with connection:
                    handle_client(connection, address, args.level, args.questions)
        except KeyboardInterrupt:
            print("\nServidor terminado.")


if __name__ == "__main__":
    main()
