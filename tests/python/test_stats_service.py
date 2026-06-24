"""[Secções 30 a 33 e 38] Testes unitários para estatísticas."""
import unittest

from services.stats_service import StatsService


class StatsServiceTests(unittest.TestCase):
    def test_basic_statistics(self):
        attempts = [
            {"level": 1, "topic": "IPv4", "is_correct": True, "response_time_seconds": 2},
            {"level": 1, "topic": "IPv4", "is_correct": False, "response_time_seconds": 4},
            {"level": 2, "topic": "Sub-redes", "is_correct": False, "response_time_seconds": 4},
        ]
        result = StatsService().calculate(attempts)
        self.assertEqual(result["total"], 3)
        self.assertEqual(result["correct"], 1)
        self.assertEqual(result["wrong"], 2)
        self.assertEqual(result["accuracy"], 33.33)
        self.assertEqual(result["accuracy_by_level"], {"1": 50.0, "2": 0.0})
        self.assertEqual(result["mean_time"], 3.33)
        self.assertEqual(result["median_time"], 4)
        self.assertEqual(result["mode_time"], 4)

    def test_weakest_topic_uses_the_topic_with_more_errors(self):
        attempts = [
            {"level": 1, "topic": "IPv4", "is_correct": False, "response_time_seconds": 2},
            {"level": 1, "topic": "IPv4", "is_correct": False, "response_time_seconds": 3},
            {"level": 4, "topic": "IPv6", "is_correct": False, "response_time_seconds": 4},
        ]
        self.assertEqual(StatsService().calculate(attempts)["weakest_topic"], "IPv4")

    def test_empty_attempts_have_safe_values(self):
        result = StatsService().calculate([])
        self.assertEqual(result["total"], 0)
        self.assertEqual(result["accuracy"], 0)
        self.assertEqual(result["mode_time"], "sem dados")

    def test_incomplete_attempt_is_ignored(self):
        # Garante que um registo manualmente danificado não bloqueia estatísticas.
        attempts = [
            {"level": 1, "topic": "IPv4", "is_correct": True, "response_time_seconds": 2},
            {"username": "sem_campos"},
        ]
        result = StatsService().calculate(attempts)
        self.assertEqual(result["total"], 1)
        self.assertEqual(result["correct"], 1)

    def test_score_quartiles(self):
        quartiles = StatsService().score_quartiles({"a": 10, "b": 20, "c": 30, "d": 40})
        self.assertEqual(quartiles, {"min": 10, "q1": 15.0, "q2": 25.0, "q3": 35.0, "max": 40})


if __name__ == "__main__":
    unittest.main()
