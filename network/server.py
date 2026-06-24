"""[Secções 35 a 37] Servidor TCP simples com mensagens JSON."""
import json
import os
import socket
import sys
import argparse

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.auth_service import AuthService
from services.game_service import GameService
from services.score_service import ScoreService
from services.stats_service import StatsService

HOST = "127.0.0.1"
# A web Flask usa 5000; o TCP usa 5001 para ambos poderem ser demonstrados.
PORT = 5001
LAST_QUESTION = None


def send_json(connection, message):
    """[Secção 36] Envia um objeto Python como uma linha JSON."""
    connection.sendall((json.dumps(message) + "\n").encode("utf-8"))


def process_message(message, client_state=None):
    """[Secção 36] Responde aos tipos de mensagem pedidos no enunciado."""
    global LAST_QUESTION
    client_state = client_state if client_state is not None else {}
    message_type = message.get("type")
    if message_type == "AUTH_REQUEST":
        valid = AuthService().login(message.get("username", ""), message.get("password", ""))
        return {"type": "AUTH_RESPONSE", "success": valid}
    if message_type == "QUESTION_REQUEST":
        question = GameService().create_question(message.get("level", 1))
        if question is None:
            return {"type": "QUESTION_PUSH", "error": "Nível sem perguntas."}
        client_state["question"] = question
        LAST_QUESTION = question  # Mantido para os testes unitários simples.
        # A resposta correta fica no servidor; o cliente recebe só o necessário.
        public_question = {key: value for key, value in question.items() if key != "correct_index"}
        return {"type": "QUESTION_PUSH", "question": public_question}
    if message_type == "ANSWER_SUBMIT":
        question = client_state.get("question", LAST_QUESTION)
        if question is None:
            return {"type": "ANSWER_RESULT", "error": "Não existe pergunta ativa."}
        correct = message.get("selected_index") == question["correct_index"]
        return {"type": "ANSWER_RESULT", "is_correct": correct}
    if message_type == "SCORE_UPDATE":
        return {"type": "SCORE_UPDATE", "message": "Score recebido."}
    if message_type == "RANKING_REQUEST":
        return {"type": "RANKING_RESPONSE", "ranking": ScoreService().top_five()}
    if message_type == "STATS_REQUEST":
        return {"type": "STATS_RESPONSE", "stats": StatsService().global_statistics()}
    if message_type == "END_SESSION":
        return {"type": "END_SESSION", "message": "Sessão terminada pelo cliente."}
    return {"type": "ERROR", "message": "Mensagem desconhecida."}


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
    parser.add_argument("--level", type=int, default=1, help="Nível preparado para a sessão")
    parser.add_argument("--questions", type=int, default=5, help="Quantidade de perguntas por sessão")
    args = parser.parse_args()
    print(f"Sessão preparada: nível {args.level}, {args.questions} perguntas por aluno.")
    main(args.host, args.port)
