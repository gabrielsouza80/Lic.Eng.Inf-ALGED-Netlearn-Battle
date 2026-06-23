"""Cálculo de estatísticas simples a partir de attempts.json."""
from collections import Counter
import statistics

from services.json_service import load


class StatsService:
    def calculate(self, attempts):
        """Calcula estatísticas de uma lista de tentativas."""
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
        attempts = [item for item in load("attempts.json", []) if item["username"] == username]
        return self.calculate(attempts)

    def global_statistics(self):
        """Calcula estatísticas de todos os alunos para a página de professor."""
        return self.calculate(load("attempts.json", []))
