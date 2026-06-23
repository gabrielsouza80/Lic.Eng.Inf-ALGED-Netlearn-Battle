"""Regras simples do jogo: perguntas JSON, tentativas e pontuação."""
import time

from services.json_service import load, save
from services.score_service import ScoreService
from structures.queue import Queue
from structures.stack import Stack


class GameService:
    def __init__(self):
        self.scores = ScoreService()

    def history_for(self, username):
        """Devolve as tentativas de um utilizador."""
        return [attempt for attempt in load("attempts.json", [])
                if attempt["username"] == username]

    def recent_attempts(self, limit=20):
        """Devolve as últimas tentativas de todos os alunos para o professor."""
        return list(reversed(load("attempts.json", [])[-limit:]))

    def create_question(self, level):
        """Carrega perguntas de JSON para uma Queue e devolve a primeira.

        Queue é FIFO: a primeira pergunta colocada é a primeira a sair.
        """
        filename = "acls.json" if level == 5 else "questions.json"
        questions = [question for question in load(filename, [])
                     if question["level"] == level]
        queue = Queue()
        for question in questions:
            queue.enqueue(question)
        return queue.dequeue()

    def save_attempt(self, username, question, selected_index, started_at):
        """Corrige uma resposta e guarda uma tentativa em attempts.json."""
        options = question["options"]
        valid_answer = 0 <= selected_index < len(options)
        correct_index = question["correct_index"]
        is_correct = valid_answer and selected_index == correct_index
        points = question["points_correct"] if is_correct else question["points_wrong"]
        selected_answer = options[selected_index] if valid_answer else "Sem resposta"

        attempt = {
            "username": username,
            "level": question["level"],
            "topic": question["topic"],
            "question": question["question"],
            "selected_answer": selected_answer,
            "correct_answer": options[correct_index],
            "is_correct": is_correct,
            "points": points,
            "response_time_seconds": round(max(0, time.time() - started_at), 2),
        }

        # Stack é LIFO: a última tentativa colocada é a primeira a sair.
        stack = Stack()
        stack.push(attempt)
        attempts = load("attempts.json", [])
        attempts.append(stack.pop())
        save("attempts.json", attempts)
        score = self.scores.add_points(username, points)
        return {"is_correct": is_correct, "points": points, "score": score,
                "correct_answer": options[correct_index]}
