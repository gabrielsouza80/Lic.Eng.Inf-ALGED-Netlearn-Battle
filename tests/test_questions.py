"""Testes pequenos para confirmar o carregamento de perguntas JSON."""
import unittest

from services.game_service import GameService


class QuestionTests(unittest.TestCase):
    def test_every_level_has_a_question(self):
        game = GameService()
        for level in (1, 2, 3, 4, 5):
            question = game.create_question(level)
            self.assertIsNotNone(question)
            self.assertEqual(question["level"], level)
            self.assertIn(question["options"][question["correct_index"]], question["options"])


if __name__ == "__main__":
    unittest.main()
