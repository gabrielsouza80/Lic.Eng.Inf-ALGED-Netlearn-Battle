"""[Secções 27, 28 e 38] Testes unitários para score e ranking."""
import os
import tempfile
import unittest

from services.score_service import ScoreService


class ScoreServiceTests(unittest.TestCase):
    def test_add_points_updates_score(self):
        # O ficheiro temporário evita alterar data/scores.json do projeto.
        with tempfile.TemporaryDirectory() as directory:
            filename = os.path.join(directory, "scores.json")
            service = ScoreService(filename)
            service.add_points("aluno_teste", 10)
            final_score = service.add_points("aluno_teste", -5)
            self.assertEqual(final_score, 5)
            self.assertEqual(service.get_score("aluno_teste"), 5)

    def test_top_five_is_ordered_by_score(self):
        with tempfile.TemporaryDirectory() as directory:
            service = ScoreService(os.path.join(directory, "scores.json"))
            for username, score in {"ana": 30, "bruno": 50, "carla": 10, "diana": 40, "edu": 20, "fabio": 60}.items():
                service.add_points(username, score)
            ranking = service.top_five()
            self.assertEqual([item["username"] for item in ranking], ["fabio", "bruno", "diana", "ana", "edu"])


if __name__ == "__main__":
    unittest.main()
