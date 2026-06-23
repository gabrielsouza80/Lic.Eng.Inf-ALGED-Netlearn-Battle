"""[Secções 35 a 37] Cliente TCP que envia mensagens JSON ao servidor."""
import json
import socket

HOST = "127.0.0.1"
# A web Flask usa 5000; este cliente liga à demonstração TCP na porta 5001.
PORT = 5001


def send_and_receive(connection, reader, message):
    """[Secção 36] Envia uma mensagem JSON e lê uma resposta JSON."""
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

        # Esta mensagem demonstra ANSWER_SUBMIT e ANSWER_RESULT.
        result = send_and_receive(client, reader, {
            "type": "ANSWER_SUBMIT",
            "selected_index": answer,
            "correct_index": question["correct_index"],
        })
        print(result)
        print(send_and_receive(client, reader, {"type": "SCORE_UPDATE"}))


if __name__ == "__main__":
    main()
