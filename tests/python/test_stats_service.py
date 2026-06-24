"""Testes unitários para estatísticas."""
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

    def test_accuracy_by_type(self):
        attempts = [
            {"level": 1, "topic": "IPv4", "is_correct": True, "response_time_seconds": 2, "question_type": "network_id"},
            {"level": 1, "topic": "IPv4", "is_correct": False, "response_time_seconds": 3, "question_type": "network_id"},
            {"level": 1, "topic": "IPv4", "is_correct": True, "response_time_seconds": 2, "question_type": "broadcast"},
        ]
        result = StatsService().accuracy_by_type(attempts)
        self.assertIn("network_id", result)
        self.assertIn("broadcast", result)
        self.assertEqual(result["network_id"], 50.0)
        self.assertEqual(result["broadcast"], 100.0)

    def test_global_statistics_returns_accuracy(self):
        result = StatsService().global_statistics()
        self.assertIn("accuracy", result)

    def test_score_quartiles_empty(self):
        quartiles = StatsService().score_quartiles({})
        self.assertEqual(quartiles, {"min": 0, "q1": 0, "q2": 0, "q3": 0, "max": 0})


if __name__ == "__main__":
    unittest.main()
