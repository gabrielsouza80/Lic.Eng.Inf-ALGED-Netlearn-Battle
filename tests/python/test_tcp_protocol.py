"""Testes das mensagens JSON da demonstração TCP."""
import tempfile
import unittest

from services import json_service
from services.json_service import save
from network.server import process_message


SAMPLE_QUESTION = {
    "level": 1, "topic": "IPv4", "question": "Teste?",
    "options": ["A", "B", "C", "D"], "correct_index": 0,
    "points_correct": 10, "points_wrong": -5,
}


class TcpProtocolTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.original_data_dir = json_service.DATA_DIR
        json_service.DATA_DIR = self.directory.name
        save("attempts.json", [])
        save("scores.json", {})
        save("questions.json", [SAMPLE_QUESTION])

    def tearDown(self):
        json_service.DATA_DIR = self.original_data_dir
        self.directory.cleanup()

    def test_auth_request_response(self):
        response = process_message({"type": "AUTH_REQUEST", "username": "inexistente", "password": "x"})
        self.assertEqual(response["type"], "AUTH_RESPONSE")
        self.assertIn("success", response)

    def test_question_request_returns_question_or_clear_error(self):
        response = process_message({"type": "QUESTION_REQUEST", "level": 1})
        self.assertEqual(response["type"], "QUESTION_PUSH")
        self.assertIn("question", response)
        self.assertEqual(response["question"]["level"], 1)
        self.assertNotIn("correct_index", response["question"])
        self.assertNotIn("points_correct", response["question"])
        self.assertNotIn("points_wrong", response["question"])
        invalid = process_message({"type": "QUESTION_REQUEST", "level": 99})
        self.assertEqual(invalid["type"], "QUESTION_PUSH")
        self.assertIn("error", invalid)

    def test_answer_result_returns_points_and_score(self):
        client_state = {}
        auth = process_message({"type": "AUTH_REQUEST", "username": "teste", "password": "x"}, client_state)
        process_message({"type": "QUESTION_REQUEST", "level": 1}, client_state)
        result = process_message({"type": "ANSWER_SUBMIT", "selected_index": 0}, client_state)
        self.assertIn("is_correct", result)
        self.assertIn("points", result)
        self.assertIn("score", result)
        self.assertIn("correct_answer", result)

    def test_score_update_returns_current_score(self):
        client_state = {"username": "teste"}
        result = process_message({"type": "SCORE_UPDATE"}, client_state)
        self.assertEqual(result["type"], "SCORE_UPDATE")
        self.assertIn("score", result)

    def test_ranking_request_returns_ranking_response(self):
        response = process_message({"type": "RANKING_REQUEST"})
        self.assertEqual(response["type"], "RANKING_RESPONSE")
        self.assertIn("ranking", response)

    def test_stats_request_returns_stats_response(self):
        response = process_message({"type": "STATS_REQUEST"})
        self.assertEqual(response["type"], "STATS_RESPONSE")
        self.assertIn("stats", response)

    def test_end_session_returns_end_session(self):
        response = process_message({"type": "END_SESSION"})
        self.assertEqual(response["type"], "END_SESSION")

    def test_invalid_message_type_returns_error(self):
        response = process_message({"type": "INVALID"})
        self.assertEqual(response["type"], "ERROR")
        self.assertIn("Mensagem desconhecida", response["message"])

    def test_question_push_never_sends_sensitive_fields(self):
        response = process_message({"type": "QUESTION_REQUEST", "level": 1})
        self.assertEqual(response["type"], "QUESTION_PUSH")
        q = response.get("question", {})
        self.assertNotIn("correct_index", q)
        self.assertNotIn("points_correct", q)
        self.assertNotIn("points_wrong", q)


if __name__ == "__main__":
    unittest.main()
