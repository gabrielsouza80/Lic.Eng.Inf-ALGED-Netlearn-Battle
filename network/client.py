"""Cliente TCP simples para demonstrar mensagens JSON ao servidor."""
import json
import socket

HOST = "127.0.0.1"
PORT = 5000


def send_and_receive(connection, reader, message):
    """Envia uma mensagem JSON e lê uma resposta JSON."""
    connection.sendall((json.dumps(message) + "\n").encode("utf-8"))
    return json.loads(reader.readline())


def main():
    with socket.create_connection((HOST, PORT)) as client:
        reader = client.makefile("r", encoding="utf-8")
        username = input("Utilizador: ")
        password = input("Password: ")
        response = send_and_receive(client, reader, {"type": "AUTH_REQUEST", "username": username, "password": password})
        print(response)
        if not response.get("success"):
            return
        question_response = send_and_receive(client, reader, {"type": "QUESTION_REQUEST", "level": 1})
        print(question_response)
        # O cliente apenas demonstra o envio de uma resposta; não é um jogo TCP completo.
        print(send_and_receive(client, reader, {"type": "SCORE_UPDATE"}))


if __name__ == "__main__":
    main()
