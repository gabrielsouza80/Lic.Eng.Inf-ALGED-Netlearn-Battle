"""Testes das mensagens JSON da demonstração TCP."""
import unittest

from network.server import process_message


class TcpProtocolTests(unittest.TestCase):
    def test_question_request_returns_question_or_clear_error(self):
        response = process_message({"type": "QUESTION_REQUEST", "level": 1})
        self.assertEqual(response["type"], "QUESTION_PUSH")
        self.assertIn("question", response)
        self.assertEqual(response["question"]["level"], 1)

        invalid = process_message({"type": "QUESTION_REQUEST", "level": 99})
        self.assertEqual(invalid["type"], "QUESTION_PUSH")
        self.assertIn("error", invalid)

    def test_answer_result_and_unknown_message(self):
        correct = process_message({"type": "ANSWER_SUBMIT", "selected_index": 1, "correct_index": 1})
        wrong = process_message({"type": "ANSWER_SUBMIT", "selected_index": 0, "correct_index": 1})
        unknown = process_message({"type": "OUTRA_MENSAGEM"})

        self.assertTrue(correct["is_correct"])
        self.assertFalse(wrong["is_correct"])
        self.assertEqual(unknown["type"], "ERROR")

    def test_score_update_has_expected_type(self):
        response = process_message({"type": "SCORE_UPDATE"})
        self.assertEqual(response["type"], "SCORE_UPDATE")


if __name__ == "__main__":
    unittest.main()
