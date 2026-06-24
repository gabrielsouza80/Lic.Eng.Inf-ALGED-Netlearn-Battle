"""Testes do servidor TCP: pergunta sem correct_index e mensagens inválidas."""
import hashlib
import secrets
import tempfile
import unittest

from services import json_service
from network import server
from services.json_service import save


SAMPLE_USER = "tcp_tester"
SAMPLE_PASS = "abc123"


def _register_user():
    salt = secrets.token_hex(16)
    pw_hash = hashlib.sha256((salt + SAMPLE_PASS).encode()).hexdigest()
    save("users.json", [{"username": SAMPLE_USER, "salt": salt, "password_hash": pw_hash}])


class TcpServerTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.original_data_dir = json_service.DATA_DIR
        json_service.DATA_DIR = self.directory.name
        save("attempts.json", [])
        save("scores.json", {})
        save("questions.json", [{"level": 1, "topic": "IPv4", "question": "Qual?",
                                  "options": ["a", "b", "c", "d"], "correct_index": 2,
                                  "points_correct": 10, "points_wrong": -5}])
        _register_user()
        self.state = {}
        server.process_message({"type": "AUTH_REQUEST", "username": SAMPLE_USER, "password": SAMPLE_PASS}, self.state)

    def tearDown(self):
        json_service.DATA_DIR = self.original_data_dir
        self.directory.cleanup()

    def test_question_push_hides_sensitive_fields(self):
        response = server.process_message({"type": "QUESTION_REQUEST", "level": 1}, self.state)
        public = response.get("question", {})
        self.assertNotIn("correct_index", public)
        self.assertNotIn("points_correct", public)
        self.assertNotIn("points_wrong", public)

    def test_unknown_message_type_returns_error(self):
        response = server.process_message({"type": "DESCONHECIDO"})
        self.assertEqual(response["type"], "ERROR")


if __name__ == "__main__":
    unittest.main()
