"""Testes pequenos para as estatísticas de tentativas."""
import unittest

from services.stats_service import StatsService


class StatsTests(unittest.TestCase):
    def test_statistics(self):
        attempts = [
            {"level": 1, "topic": "IPv4", "is_correct": True, "response_time_seconds": 2},
            {"level": 1, "topic": "IPv4", "is_correct": False, "response_time_seconds": 4},
            {"level": 2, "topic": "Sub-redes", "is_correct": False, "response_time_seconds": 4},
        ]
        result = StatsService().calculate(attempts)
        self.assertEqual(result["total"], 3)
        self.assertEqual(result["correct"], 1)
        self.assertEqual(result["accuracy"], 33.33)
        self.assertEqual(result["median_time"], 4)
        self.assertEqual(result["mode_time"], 4)
        self.assertEqual(result["weakest_topic"], "IPv4")


if __name__ == "__main__":
    unittest.main()
