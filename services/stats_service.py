"""[Secções 30 a 33] Estatísticas calculadas a partir de attempts.json."""
from collections import Counter
import statistics

from services.json_service import load


class StatsService:
    def calculate(self, attempts):
        """[Secções 30 a 33] Calcula estatísticas de uma lista de tentativas."""
        # attempts.json é persistência simples. Se um registo estiver incompleto,
        # ele não entra no cálculo, mas os restantes dados continuam disponíveis.
        attempts = [attempt for attempt in attempts
                    if isinstance(attempt, dict)
                    and isinstance(attempt.get("is_correct"), bool)
                    and isinstance(attempt.get("level"), int)
                    and isinstance(attempt.get("topic"), str)
                    and isinstance(attempt.get("response_time_seconds"), (int, float))
                    and not isinstance(attempt.get("response_time_seconds"), bool)]
        if not attempts:
            return {"total": 0, "correct": 0, "wrong": 0, "accuracy": 0,
                    "accuracy_by_level": {}, "mean_time": 0, "median_time": 0,
                    "mode_time": "sem dados", "weakest_topic": "sem dados"}

        correct = sum(attempt["is_correct"] for attempt in attempts)
        times = [attempt["response_time_seconds"] for attempt in attempts]
        accuracy_by_level = {}
        errors_by_topic = {}

        for level in sorted({attempt["level"] for attempt in attempts}):
            level_attempts = [item for item in attempts if item["level"] == level]
            level_correct = sum(item["is_correct"] for item in level_attempts)
            accuracy_by_level[str(level)] = round(100 * level_correct / len(level_attempts), 2)

        for attempt in attempts:
            if not attempt["is_correct"]:
                topic = attempt["topic"]
                errors_by_topic[topic] = errors_by_topic.get(topic, 0) + 1

        occurrences = Counter(times)
        mode = max(occurrences, key=occurrences.get)
        mode_time = mode if occurrences[mode] > 1 else "sem moda"
        weakest_topic = max(errors_by_topic, key=errors_by_topic.get) if errors_by_topic else "nenhum"

        return {"total": len(attempts), "correct": correct, "wrong": len(attempts) - correct,
                "accuracy": round(100 * correct / len(attempts), 2),
                "accuracy_by_level": accuracy_by_level,
                "mean_time": round(statistics.mean(times), 2),
                "median_time": round(statistics.median(times), 2),
                "mode_time": mode_time, "weakest_topic": weakest_topic}

    def personal_statistics(self, username):
        # [Secção 30] Filtra as tentativas para mostrar só dados do aluno.
        attempts = [item for item in load("attempts.json", [])
                    if isinstance(item, dict) and item.get("username") == username]
        return self.calculate(attempts)

    def score_evolution(self, username):
        """Agrupa tentativas por sessão para a tabela de evolução do aluno."""
        sessions = {}
        for attempt in self.history_for_user(username):
            session_id = attempt.get("session_id", "sem_sessao")
            item = sessions.setdefault(session_id, {"session_id": session_id,
                "date": attempt.get("created_at", "sem data"), "points": 0, "score": 0})
            item["points"] += attempt.get("points", 0)
            item["score"] = attempt.get("score_after_attempt", item["score"])
        return list(sessions.values())

    def history_for_user(self, username):
        return [item for item in load("attempts.json", [])
                if isinstance(item, dict) and item.get("username") == username]

    def global_statistics(self):
        """[Secção 34] Calcula estatísticas gerais para a área do professor."""
        return self.calculate(load("attempts.json", []))

    def score_quartiles(self, scores):
        """Calcula mínimo, Q1, mediana/Q2, Q3 e máximo de forma simples."""
        values = sorted(value for value in scores.values() if isinstance(value, (int, float)))
        if not values:
            return {"min": 0, "q1": 0, "q2": 0, "q3": 0, "max": 0}
        middle = len(values) // 2
        lower = values[:middle] or values
        upper = values[middle + (len(values) % 2):] or values
        return {"min": values[0], "q1": statistics.median(lower),
                "q2": statistics.median(values), "q3": statistics.median(upper),
                "max": values[-1]}

    def accuracy_by_type(self, attempts):
        """Agrupa tentativas por question_type; perguntas antigas usam 'geral'."""
        groups = {}
        for attempt in attempts:
            if isinstance(attempt, dict):
                key = attempt.get("question_type", "geral")
                groups.setdefault(key, []).append(attempt)
        return {name: round(100 * sum(item.get("is_correct", False) for item in items) / len(items), 2)
                for name, items in groups.items()}
