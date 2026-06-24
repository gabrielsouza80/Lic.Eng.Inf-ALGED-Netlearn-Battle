"""Servidor TCP do NetLearn Battle.

Mensagens do protocolo:
  AUTH_REQUEST     -> AUTH_RESPONSE
  QUESTION_REQUEST -> QUESTION_PUSH
  ANSWER_SUBMIT    -> ANSWER_RESULT
  RANKING_REQUEST  -> RANKING_RESPONSE
  STATS_REQUEST    -> STATS_RESPONSE
  END_SESSION      -> END_SESSION
"""
import json
import os
import socket
import sys
import time
import argparse

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.auth_service import AuthService
from services.game_service import GameService
from services.score_service import ScoreService
from services.stats_service import StatsService

HOST = "127.0.0.1"
PORT = 5001


def send_json(connection, message):
    connection.sendall((json.dumps(message) + "\n").encode("utf-8"))


def process_message(message, client_state=None):
    client_state = client_state if client_state is not None else {}
    message_type = message.get("type")
    try:
        if message_type == "AUTH_REQUEST":
            valid = AuthService().login(message.get("username", ""), message.get("password", ""))
            if valid:
                client_state["username"] = message.get("username", "")
            return {"type": "AUTH_RESPONSE", "success": valid}

        if message_type == "QUESTION_REQUEST":
            if "username" not in client_state:
                return {"type": "ERROR", "message": "Autenticação necessária."}
            question = GameService().create_question(message.get("level", 1))
            if question is None:
                return {"type": "QUESTION_PUSH", "error": "Nível sem perguntas."}
            client_state["question"] = question
            client_state["started_at"] = time.time()
            allowed_keys = {"question", "options", "level", "topic", "question_type"}
            public_question = {key: question[key] for key in allowed_keys if key in question}
            return {"type": "QUESTION_PUSH", "question": public_question}

        if message_type == "ANSWER_SUBMIT":
            if "username" not in client_state:
                return {"type": "ERROR", "message": "Autenticação necessária."}
            question = client_state.pop("question", None)
            if question is None:
                return {"type": "ANSWER_RESULT", "error": "Não existe pergunta ativa."}
            username = client_state["username"]
            selected_index = message.get("selected_index", -1)
            started_at = client_state.get("started_at", time.time())
            result = GameService().save_attempt(username, question, selected_index, started_at, "tcp")
            return {"type": "ANSWER_RESULT", "is_correct": result["is_correct"],
                    "points": result["points"], "correct_answer": result["correct_answer"],
                    "score": result["score"]}

        if message_type == "SCORE_UPDATE":
            if "username" not in client_state:
                return {"type": "ERROR", "message": "Autenticação necessária."}
            score = ScoreService().get_score(client_state["username"])
            return {"type": "SCORE_UPDATE", "score": score}

        if message_type == "RANKING_REQUEST":
            return {"type": "RANKING_RESPONSE", "ranking": ScoreService().top_five()}
        if message_type == "STATS_REQUEST":
            return {"type": "STATS_RESPONSE", "stats": StatsService().global_statistics()}
        if message_type == "END_SESSION":
            return {"type": "END_SESSION", "message": "Sessão terminada pelo cliente."}
        return {"type": "ERROR", "message": "Mensagem desconhecida."}
    except ValueError:
        return {"type": "ERROR", "message": "Erro interno: JSON pode estar corrompido."}


def main(host=HOST, port=PORT):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((host, port))
        server.listen()
        print(f"Servidor TCP em {host}:{port}")
        while True:
            connection, address = server.accept()
            with connection:
                # Cada ligação tem a própria pergunta ativa; não partilha estado.
                client_state = {}
                print(f"Cliente ligado: {address}")
                file = connection.makefile("r", encoding="utf-8")
                for line in file:
                    try:
                        message = json.loads(line)
                    except json.JSONDecodeError:
                        # Um cliente com JSON inválido recebe erro, sem terminar o servidor.
                        send_json(connection, {"type": "ERROR", "message": "JSON inválido."})
                        continue
                    send_json(connection, process_message(message, client_state))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Servidor TCP NetLearn Battle")
    parser.add_argument("--host", default=HOST)
    parser.add_argument("--port", type=int, default=PORT)
    args = parser.parse_args()
    main(args.host, args.port)
