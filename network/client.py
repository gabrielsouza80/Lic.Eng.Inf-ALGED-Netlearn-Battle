"""[Secções 35 a 37] Cliente TCP que envia mensagens JSON ao servidor."""
import json
import socket
import argparse

HOST = "127.0.0.1"
# A web Flask usa 5000; este cliente liga à demonstração TCP na porta 5001.
PORT = 5001


def send_and_receive(connection, reader, message):
    """[Secção 36] Envia uma mensagem JSON e lê uma resposta JSON."""
    connection.sendall((json.dumps(message) + "\n").encode("utf-8"))
    return json.loads(reader.readline())


def main(host=HOST, port=PORT):
    with socket.create_connection((host, port), timeout=10) as client:
        reader = client.makefile("r", encoding="utf-8")
        username = input("Utilizador: ")
        password = input("Password: ")
        response = send_and_receive(client, reader, {"type": "AUTH_REQUEST", "username": username, "password": password})
        print(response)
        if not response.get("success"):
            return
        question_response = send_and_receive(client, reader, {"type": "QUESTION_REQUEST", "level": 1})
        question = question_response.get("question")
        if question is None:
            print(question_response)
            return

        print(question["question"])
        for index, option in enumerate(question["options"], 1):
            print(f"{index}. {option}")
        try:
            answer = int(input("Resposta: ")) - 1
        except ValueError:
            answer = -1

        # O cliente envia somente a opção escolhida. A resposta certa fica no servidor.
        result = send_and_receive(client, reader, {
            "type": "ANSWER_SUBMIT",
            "selected_index": answer,
        })
        print(result)
        print(send_and_receive(client, reader, {"type": "SCORE_UPDATE"}))
        print(send_and_receive(client, reader, {"type": "END_SESSION"}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Cliente TCP NetLearn Battle")
    parser.add_argument("--host", default=HOST)
    parser.add_argument("--port", type=int, default=PORT)
    args = parser.parse_args()
    main(args.host, args.port)
