"""[Secções 35 a 37] Servidor TCP simples com mensagens JSON."""
import json
import os
import socket
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.auth_service import AuthService
from services.game_service import GameService

HOST = "127.0.0.1"
# A web Flask usa 5000; o TCP usa 5001 para ambos poderem ser demonstrados.
PORT = 5001


def send_json(connection, message):
    """[Secção 36] Envia um objeto Python como uma linha JSON."""
    connection.sendall((json.dumps(message) + "\n").encode("utf-8"))


def process_message(message):
    """[Secção 36] Responde aos tipos de mensagem pedidos no enunciado."""
    message_type = message.get("type")
    if message_type == "AUTH_REQUEST":
        valid = AuthService().login(message.get("username", ""), message.get("password", ""))
        return {"type": "AUTH_RESPONSE", "success": valid}
    if message_type == "QUESTION_REQUEST":
        question = GameService().create_question(message.get("level", 1))
        if question is None:
            return {"type": "QUESTION_PUSH", "error": "Nível sem perguntas."}
        return {"type": "QUESTION_PUSH", "question": question}
    if message_type == "ANSWER_SUBMIT":
        # É uma demonstração simples: num servidor real a resposta certa não viria do cliente.
        correct = message.get("selected_index") == message.get("correct_index")
        return {"type": "ANSWER_RESULT", "is_correct": correct}
    if message_type == "SCORE_UPDATE":
        return {"type": "SCORE_UPDATE", "message": "Score recebido."}
    return {"type": "ERROR", "message": "Mensagem desconhecida."}


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((HOST, PORT))
        server.listen()
        print(f"Servidor TCP em {HOST}:{PORT}")
        while True:
            connection, address = server.accept()
            with connection:
                print(f"Cliente ligado: {address}")
                file = connection.makefile("r", encoding="utf-8")
                for line in file:
                    try:
                        message = json.loads(line)
                    except json.JSONDecodeError:
                        # Um cliente com JSON inválido recebe erro, sem terminar o servidor.
                        send_json(connection, {"type": "ERROR", "message": "JSON inválido."})
                        continue
                    send_json(connection, process_message(message))


if __name__ == "__main__":
    main()
