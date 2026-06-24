"""Testes das mensagens JSON da demonstração TCP."""
import unittest

from network.server import process_message


class TcpProtocolTests(unittest.TestCase):
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

    def test_answer_result_and_unknown_message(self):
        question = process_message({"type": "QUESTION_REQUEST", "level": 1})["question"]
        correct = process_message({"type": "ANSWER_SUBMIT", "selected_index": 0})
        wrong = process_message({"type": "ANSWER_SUBMIT", "selected_index": 99})
        unknown = process_message({"type": "OUTRA_MENSAGEM"})

        self.assertIn("is_correct", correct)
        self.assertIn("is_correct", wrong)
        self.assertEqual(unknown["type"], "ERROR")

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

    def test_value_error_in_process_returns_error(self):
        response = process_message({"type": "RANKING_REQUEST"})
        self.assertIn(response["type"], ("RANKING_RESPONSE", "ERROR"))

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
