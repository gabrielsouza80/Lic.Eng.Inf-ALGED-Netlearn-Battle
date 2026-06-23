"""Teste unitário simples para atualização de score."""
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


if __name__ == "__main__":
    unittest.main()
