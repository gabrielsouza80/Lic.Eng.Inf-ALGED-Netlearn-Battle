"""Testes da construção de sessões e da Stack de tentativas."""
import unittest

from services.game_service import GameService, SESSION_SIZE


class GameServiceTests(unittest.TestCase):
    def setUp(self):
        self.game = GameService()

    def test_build_session_has_correct_size_and_valid_questions(self):
        questions = self.game.build_session_questions(1)
        self.assertEqual(len(questions), SESSION_SIZE)
        for question in questions:
            self.assertEqual(len(question["options"]), 4)
            self.assertTrue(0 <= question["correct_index"] < 4)

    def test_check_training_answer_does_not_need_score(self):
        question = {"options": ["a", "b", "c", "d"], "correct_index": 2}
        right = self.game.check_training_answer(question, 2)
        wrong = self.game.check_training_answer(question, 0)
        self.assertTrue(right["is_correct"])
        self.assertFalse(wrong["is_correct"])
        self.assertEqual(right["correct_answer"], "c")


if __name__ == "__main__":
    unittest.main()
