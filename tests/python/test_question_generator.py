"""Testes do gerador de perguntas IPv4/IPv6."""
import unittest
from services.question_generator import generate_network_question


class QuestionGeneratorTests(unittest.TestCase):
    def test_generates_level_1_question(self):
        question = generate_network_question(1)
        self.assertIsNotNone(question)
        self.assertEqual(question["level"], 1)
        self.assertIn("topic", question)
        self.assertIn("question", question)
        self.assertIn("options", question)
        self.assertIn("correct_index", question)
        self.assertGreaterEqual(len(question["options"]), 2)

    def test_generates_level_2_question(self):
        question = generate_network_question(2)
        self.assertIsNotNone(question)
        self.assertEqual(question["level"], 2)

    def test_generates_level_3_question(self):
        question = generate_network_question(3)
        self.assertIsNotNone(question)
        self.assertEqual(question["level"], 3)

    def test_generates_level_4_ipv6_question(self):
        question = generate_network_question(4)
        self.assertIsNotNone(question)
        self.assertEqual(question["level"], 4)

    def test_returns_none_for_invalid_level(self):
        self.assertIsNone(generate_network_question(99))

    def test_question_has_points(self):
        question = generate_network_question(1)
        self.assertIn("points_correct", question)
        self.assertIn("points_wrong", question)

    def test_question_type_is_present(self):
        question = generate_network_question(1)
        self.assertIn("question_type", question)

    def test_all_levels_produce_valid_questions(self):
        for level in (1, 2, 3, 4):
            question = generate_network_question(level)
            self.assertIsNotNone(question, f"Level {level} returned None")
            self.assertIsInstance(question["options"], list)
            self.assertGreaterEqual(len(question["options"]), 2)
            self.assertIn(question["correct_index"], range(len(question["options"])),
                          f"Level {level}: correct_index out of range")

    def test_options_have_no_generic_labels(self):
        for level in (1, 2, 3):
            question = generate_network_question(level)
            for option in question["options"]:
                self.assertNotIn("opção", option.lower())
                self.assertNotIn("option", option.lower())

    def test_same_network_can_produce_sim_and_nao(self):
        results = {"Sim": False, "Não": False}
        for _ in range(50):
            question = generate_network_question(1)
            if question["question_type"] == "same_network":
                correct = question["options"][question["correct_index"]]
                results[correct] = True
            if all(results.values()):
                break
        self.assertTrue(results["Sim"], "Same network deve gerar Sim")
        self.assertTrue(results["Não"], "Same network deve gerar Não")


if __name__ == "__main__":
    unittest.main()
