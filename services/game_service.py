"""[Secções 14, 15, 24, 25 e 27] Regras principais do jogo."""
import time

from services.json_service import load, save
from services.score_service import ScoreService
from structures.queue import Queue
from structures.stack import Stack


class GameService:
    def __init__(self):
        self.scores = ScoreService()

    def history_for(self, username):
        """[Secção 29] Devolve as tentativas de um utilizador."""
        # .get evita falha caso exista uma tentativa antiga/incompleta no JSON.
        return [attempt for attempt in load("attempts.json", [])
                if isinstance(attempt, dict) and attempt.get("username") == username]

    def recent_attempts(self, limit=20):
        """Devolve as últimas tentativas de todos os alunos para o professor."""
        attempts = [attempt for attempt in load("attempts.json", []) if isinstance(attempt, dict)]
        return list(reversed(attempts[-limit:]))

    def create_question(self, level):
        """[Secções 14 e 24] Carrega perguntas para Queue e devolve a primeira.

        Queue é FIFO: a primeira pergunta colocada é a primeira a sair.
        """
        filename = "acls.json" if level == 5 else "questions.json"
        # As perguntas são conteúdo controlado do projeto. Ainda assim, ignoramos
        # uma entrada incompleta para a página não falhar por uma edição manual.
        required_fields = {"level", "topic", "question", "options", "correct_index",
                           "points_correct", "points_wrong"}
        questions = [question for question in load(filename, [])
                     if isinstance(question, dict)
                     and required_fields.issubset(question)
                     and isinstance(question.get("options"), list)
                     and question.get("level") == level]
        queue = Queue()
        for question in questions:
            queue.enqueue(question)
        return queue.dequeue()

    def save_attempt(self, username, question, selected_index, started_at):
        """[Secções 14, 25 e 27] Corrige e guarda uma tentativa."""
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

        # [Secção 25] Stack é LIFO: a última tentativa entra e sai primeiro.
        stack = Stack()
        stack.push(attempt)
        attempts = load("attempts.json", [])
        if not isinstance(attempts, list):
            raise ValueError("attempts.json deve conter uma lista de tentativas.")
        attempts.append(stack.pop())
        save("attempts.json", attempts)
        score = self.scores.add_points(username, points)
        return {"is_correct": is_correct, "points": points, "score": score,
                "correct_answer": options[correct_index]}
