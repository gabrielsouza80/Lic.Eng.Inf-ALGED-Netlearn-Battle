"""Cliente TCP do NetLearn Battle.

Liga-se ao servidor, autentica o aluno e joga uma sessão completa de perguntas
trocando mensagens JSON (uma por linha). O cliente nunca recebe o índice da
resposta correta antes de responder: é o servidor que valida.
"""
import argparse
import json
import socket


def send_and_receive(connection, reader, message):
    """Envia uma mensagem JSON e devolve a resposta JSON do servidor."""
    connection.sendall((json.dumps(message) + "\n").encode("utf-8"))
    line = reader.readline()
    if not line:
        raise ConnectionError("O servidor fechou a ligação.")
    return json.loads(line)


def play_question(connection, reader, question):
    """Mostra uma pergunta, lê a escolha do aluno e devolve o resultado."""
    print(f"\nPergunta {question['position']}/{question['total']} "
          f"(nível {question['level']} · {question['topic']})")
    print(question["question"])
    for index, option in enumerate(question["options"]):
        print(f"  [{index}] {option}")
    try:
        selected = int(input("Resposta (número): "))
    except ValueError:
        selected = -1
    result = send_and_receive(connection, reader,
                              {"type": "ANSWER", "selected_index": selected})
    estado = "CERTA" if result["is_correct"] else "ERRADA"
    print(f"-> {estado}. Correta: {result['correct_answer']}. "
          f"{result['points']:+d} pontos (score {result['score']}).")


def main():
    parser = argparse.ArgumentParser(description="Cliente TCP do NetLearn Battle.")
    parser.add_argument("--host", default="127.0.0.1", help="Endereço do servidor.")
    parser.add_argument("--port", type=int, default=5001, help="Porta do servidor.")
    parser.add_argument("--level", type=int, default=1, help="Nível a jogar.")
    args = parser.parse_args()

    try:
        with socket.create_connection((args.host, args.port)) as client:
            reader = client.makefile("r", encoding="utf-8")

            username = input("Utilizador: ")
            password = input("Password: ")
            auth = send_and_receive(client, reader,
                                    {"type": "AUTH", "username": username, "password": password})
            print(auth.get("message", ""))
            if not auth.get("success"):
                return

            response = send_and_receive(client, reader, {"type": "START", "level": args.level})
            while response.get("type") == "QUESTION":
                play_question(client, reader, response)
                response = send_and_receive(client, reader, {"type": "NEXT"})

            if response.get("type") == "END":
                print(f"\nSessão terminada: {response['correct']}/{response['total']} certas, "
                      f"{response['session_points']:+d} pontos. Score final: {response['final_score']}.")
            elif response.get("type") == "ERROR":
                print(f"Erro: {response.get('message')}")

            ranking = send_and_receive(client, reader, {"type": "RANKING"})
            print("\nTop 5:")
            for item in ranking.get("ranking", []):
                print(f"  {item['username']}: {item['score']} pontos")
    except (ConnectionError, OSError) as error:
        print(f"Não foi possível comunicar com o servidor: {error}")


if __name__ == "__main__":
    main()
