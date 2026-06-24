"""Testes da lógica ACL e da primeira regra compatível."""
import unittest
from services.acl_service import (evaluate_acl, generate_acl_question,
                                  generate_acl_first_match_question,
                                  generate_acl_order_question, generate_acl_missing_ace_question,
                                  generate_acl_for_server_question)


RULES = [
    {"id": "R1", "action": "deny", "protocol": "tcp", "src": "any", "dst": "192.168.1.10/32", "port": 22},
    {"id": "R2", "action": "permit", "protocol": "tcp", "src": "any", "dst": "192.168.1.10/32", "port": 80},
    {"id": "R3", "action": "deny", "protocol": "ip", "src": "any", "dst": "any", "port": "any"},
]


class AclServiceTests(unittest.TestCase):
    def test_permit_and_first_match(self):
        packet = {"src_ip": "10.0.0.5", "dst_ip": "192.168.1.10", "protocol": "tcp", "port": 80}
        result = evaluate_acl(RULES, packet)
        self.assertEqual(result["action"], "permit")
        self.assertEqual(result["matched_rule_id"], "R2")

    def test_deny_when_first_rule_matches_ssh(self):
        packet = {"src_ip": "10.0.0.5", "dst_ip": "192.168.1.10", "protocol": "tcp", "port": 22}
        result = evaluate_acl(RULES, packet)
        self.assertEqual(result["action"], "deny")
        self.assertEqual(result["matched_rule_id"], "R1")

    def test_default_deny_when_no_rule_matches(self):
        allow_only_http = [
            {"id": "R1", "action": "permit", "protocol": "tcp", "src": "any", "dst": "192.168.1.10/32", "port": 80},
        ]
        packet = {"src_ip": "10.0.0.5", "dst_ip": "192.168.1.10", "protocol": "tcp", "port": 443}
        self.assertEqual(evaluate_acl(allow_only_http, packet)["action"], "deny")
        self.assertIsNone(evaluate_acl(allow_only_http, packet)["matched_rule_id"])

    def test_acl_question_generators_have_four_options(self):
        packet = {"src_ip": "10.0.0.5", "dst_ip": "192.168.1.10", "protocol": "tcp", "port": 80}
        questions = [generate_acl_first_match_question(RULES, packet),
                     generate_acl_order_question(), generate_acl_missing_ace_question(),
                     generate_acl_for_server_question()]
        for question in questions:
            self.assertGreaterEqual(len(question["options"]), 2)
            self.assertIn(question["correct_index"], range(len(question["options"])))
        self.assertIn("R1", questions[0]["options"])
        self.assertIn("R2", questions[0]["options"])
        self.assertIn("R3", questions[0]["options"])
        self.assertIn("Nenhuma regra", questions[0]["options"])

    def test_acl_permit_deny_question_has_two_options(self):
        question = generate_acl_question()
        if question is not None:
            self.assertEqual(len(question["options"]), 2)
            self.assertIn(question["correct_index"], (0, 1))

    def test_evaluate_acl_default_deny_with_empty_rules(self):
        result = evaluate_acl([], {"src_ip": "10.0.0.1", "dst_ip": "10.0.0.2", "protocol": "tcp", "port": 80})
        self.assertEqual(result["action"], "deny")
        self.assertIsNone(result["matched_rule_id"])
