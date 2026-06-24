"""Testes do servidor TCP: pergunta sem correct_index e mensagens inválidas."""
import tempfile
import unittest

from services import json_service
from network import server
from services.json_service import save


class TcpServerTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.original_data_dir = json_service.DATA_DIR
        json_service.DATA_DIR = self.directory.name
        save("attempts.json", [])
        save("scores.json", {})

    def tearDown(self):
        json_service.DATA_DIR = self.original_data_dir
        self.directory.cleanup()

    def test_question_push_hides_sensitive_fields(self):
        question = {"level": 1, "topic": "IPv4", "question": "Qual?",
                    "options": ["a", "b", "c", "d"], "correct_index": 2,
                    "points_correct": 10, "points_wrong": -5}
        client_state = {}
        server.LAST_QUESTION = None
        response = server.process_message(
            {"type": "QUESTION_REQUEST", "level": 1}, client_state)
        public = response.get("question", {})
        self.assertNotIn("correct_index", public)
        self.assertNotIn("points_correct", public)
        self.assertNotIn("points_wrong", public)

    def test_unknown_message_type_returns_error(self):
        response = server.process_message({"type": "DESCONHECIDO"})
        self.assertEqual(response["type"], "ERROR")


if __name__ == "__main__":
    unittest.main()
