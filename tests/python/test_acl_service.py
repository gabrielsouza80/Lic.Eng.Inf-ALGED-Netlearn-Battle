"""Testes da lógica ACL e da primeira regra compatível."""
import unittest
from services.acl_service import (evaluate_acl, generate_acl_first_match_question,
                                  generate_acl_order_question, generate_acl_missing_ace_question,
                                  generate_acl_for_server_question)


RULES = [
    {"id": "R1", "action": "deny", "protocol": "tcp", "src": "any", "dst": "192.168.1.10/32", "port": 22},
    {"id": "R2", "action": "permit", "protocol": "tcp", "src": "any", "dst": "192.168.1.10/32", "port": 80},
]


class AclServiceTests(unittest.TestCase):
    def test_permit_and_first_match(self):
        packet = {"src_ip": "10.0.0.5", "dst_ip": "192.168.1.10", "protocol": "tcp", "port": 80}
        result = evaluate_acl(RULES, packet)
        self.assertEqual(result["action"], "permit")
        self.assertEqual(result["matched_rule_id"], "R2")

    def test_default_deny(self):
        packet = {"src_ip": "10.0.0.5", "dst_ip": "192.168.1.10", "protocol": "tcp", "port": 443}
        self.assertEqual(evaluate_acl(RULES, packet)["action"], "deny")

    def test_acl_question_generators_have_four_options(self):
        packet = {"src_ip": "10.0.0.5", "dst_ip": "192.168.1.10", "protocol": "tcp", "port": 80}
        questions = [generate_acl_first_match_question(RULES, packet),
                     generate_acl_order_question(), generate_acl_missing_ace_question(),
                     generate_acl_for_server_question()]
        for question in questions:
            self.assertEqual(len(question["options"]), 4)
            self.assertIn(question["correct_index"], range(4))
