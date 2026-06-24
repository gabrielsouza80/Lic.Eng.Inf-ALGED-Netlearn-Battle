"""Testes unitários simples do GameService e da persistência de tentativas."""
import tempfile
import time
import unittest

from services import json_service
from services.game_service import GameService
from services.json_service import load, save


QUESTION = {
    "level": 1,
    "topic": "IPv4",
    "question": "Pergunta de teste",
    "options": ["Certa", "Errada"],
    "correct_index": 0,
    "points_correct": 10,
    "points_wrong": -5,
}


class GameServiceTests(unittest.TestCase):
    def setUp(self):
        # Cada teste usa uma pasta temporária, nunca data/ do projeto.
        self.directory = tempfile.TemporaryDirectory()
        self.original_data_dir = json_service.DATA_DIR
        json_service.DATA_DIR = self.directory.name
        self.service = GameService()

    def tearDown(self):
        json_service.DATA_DIR = self.original_data_dir
        self.directory.cleanup()

    def test_create_question_returns_first_question_of_level(self):
        second_question = QUESTION.copy()
        second_question["question"] = "Segunda pergunta"
        save("questions.json", [QUESTION, second_question])
        save("acls.json", [])

        question = self.service.create_question(1)
        self.assertEqual(question["question"], "Pergunta de teste")
        self.assertIsNone(self.service.create_question(99))

    def test_save_attempt_updates_json_and_score(self):
        save("attempts.json", [])
        save("scores.json", {})

        correct = self.service.save_attempt("ana", QUESTION, 0, time.time() - 1)
        wrong = self.service.save_attempt("ana", QUESTION, 1, time.time() - 1)
        attempts = load("attempts.json", [])

        self.assertTrue(correct["is_correct"])
        self.assertEqual(correct["points"], 10)
        self.assertFalse(wrong["is_correct"])
        self.assertEqual(wrong["points"], -5)
        self.assertEqual(wrong["score"], 5)
        self.assertEqual(attempts[1]["selected_answer"], "Errada")
        self.assertEqual(attempts[1]["correct_answer"], "Certa")


if __name__ == "__main__":
    unittest.main()
