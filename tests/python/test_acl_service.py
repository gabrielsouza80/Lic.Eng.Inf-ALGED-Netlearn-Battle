"""Testes do motor de ACL (regras, pacotes e primeira correspondência)."""
import unittest

from services import acl_service


class AclServiceTests(unittest.TestCase):
    def setUp(self):
        self.rules = [
            {"id": "R1", "action": "permit", "protocol": "tcp", "src": "any",
             "dst": "192.168.1.10/32", "port": 80},
            {"id": "R2", "action": "deny", "protocol": "any", "src": "any",
             "dst": "any", "port": "any"},
        ]

    def test_rule_matches_packet(self):
        packet = {"src_ip": "10.0.0.1", "dst_ip": "192.168.1.10", "protocol": "tcp", "port": 80}
        self.assertTrue(acl_service.rule_matches_packet(self.rules[0], packet))

    def test_first_match_wins(self):
        packet = {"src_ip": "10.0.0.1", "dst_ip": "192.168.1.10", "protocol": "tcp", "port": 80}
        result = acl_service.evaluate_acl(self.rules, packet)
        self.assertEqual(result["action"], "permit")
        self.assertEqual(result["matched_rule_id"], "R1")

    def test_implicit_deny(self):
        packet = {"src_ip": "10.0.0.1", "dst_ip": "8.8.8.8", "protocol": "udp", "port": 53}
        result = acl_service.evaluate_acl([self.rules[0]], packet)
        self.assertEqual(result["action"], "deny")
        self.assertIsNone(result["matched_rule_id"])

    def test_generators_have_four_valid_options(self):
        for generator in acl_service.ACL_GENERATORS:
            question = generator()
            options = question["options"]
            self.assertTrue(2 <= len(options) <= 4)
            self.assertTrue(0 <= question["correct_index"] < len(options))
            self.assertEqual(question["level"], 5)


if __name__ == "__main__":
    unittest.main()
