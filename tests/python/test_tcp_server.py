"""Testes do servidor TCP: pergunta pública e mensagens inválidas."""
import unittest

from network import server


class TcpServerTests(unittest.TestCase):
    def test_public_question_hides_correct_index(self):
        question = {"level": 1, "topic": "IPv4", "question": "Qual?",
                    "options": ["a", "b", "c", "d"], "correct_index": 2,
                    "points_correct": 10, "points_wrong": -5}
        public = server.public_question(question, 1, 5)
        self.assertNotIn("correct_index", public)
        self.assertNotIn("points_correct", public)
        self.assertEqual(public["options"], ["a", "b", "c", "d"])

    def test_unknown_message_type_returns_error(self):
        response = server.process_message(None, {"type": "DESCONHECIDO"})
        self.assertEqual(response["type"], "ERROR")


if __name__ == "__main__":
    unittest.main()
