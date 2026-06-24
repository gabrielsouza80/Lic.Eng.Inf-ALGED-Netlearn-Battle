"""Cálculo de estatísticas a partir de attempts.json, sessions.json e scores.json."""
from collections import Counter
import statistics

from services.json_service import load


class StatsService:
    def calculate(self, attempts):
        """Calcula estatísticas de uma lista de tentativas."""
        if not attempts:
            return {"total": 0, "correct": 0, "wrong": 0, "accuracy": 0,
                    "accuracy_by_level": {}, "accuracy_by_type": {},
                    "mean_time": 0, "median_time": 0, "mode_time": "sem dados",
                    "weakest_topic": "sem dados"}

        correct = sum(attempt["is_correct"] for attempt in attempts)
        times = [attempt["response_time_seconds"] for attempt in attempts]
        accuracy_by_level = {}
        accuracy_by_type = {}
        errors_by_topic = {}

        for level in sorted({attempt["level"] for attempt in attempts}):
            level_attempts = [item for item in attempts if item["level"] == level]
            level_correct = sum(item["is_correct"] for item in level_attempts)
            accuracy_by_level[str(level)] = round(100 * level_correct / len(level_attempts), 2)

        for qtype in sorted({attempt.get("question_type", "fixa") for attempt in attempts}):
            type_attempts = [item for item in attempts if item.get("question_type", "fixa") == qtype]
            type_correct = sum(item["is_correct"] for item in type_attempts)
            accuracy_by_type[qtype] = round(100 * type_correct / len(type_attempts), 2)

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
                "accuracy_by_type": accuracy_by_type,
                "mean_time": round(statistics.mean(times), 2),
                "median_time": round(statistics.median(times), 2),
                "mode_time": mode_time, "weakest_topic": weakest_topic}

    def personal_statistics(self, username):
        """Estatísticas completas de um aluno, incluindo evolução por sessão."""
        attempts = [item for item in load("attempts.json", []) if item["username"] == username]
        result = self.calculate(attempts)
        result["score_evolution"] = self.score_evolution(username)
        return result

    def global_statistics(self):
        """Calcula estatísticas de todos os alunos para a página de professor."""
        return self.calculate(load("attempts.json", []))

    def score_evolution(self, username):
        """Devolve a lista de sessões do aluno (sessão, data, pontos, score final)."""
        return [session for session in load("sessions.json", [])
                if session.get("username") == username]

    def score_quartiles(self):
        """Calcula quartis (Q1, Q2, Q3) e o mínimo/máximo dos scores guardados."""
        values = sorted(load("scores.json", {}).values())
        if not values:
            return {"q1": 0, "q2": 0, "q3": 0, "minimum": 0, "maximum": 0, "count": 0}
        if len(values) == 1:
            single = values[0]
            return {"q1": single, "q2": single, "q3": single,
                    "minimum": single, "maximum": single, "count": 1}
        # quantiles com n=4 divide os dados em quatro partes: Q1, Q2 (mediana), Q3.
        q1, q2, q3 = statistics.quantiles(values, n=4)
        return {"q1": round(q1, 2), "q2": round(q2, 2), "q3": round(q3, 2),
                "minimum": values[0], "maximum": values[-1], "count": len(values)}
