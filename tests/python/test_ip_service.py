"""Testes do motor de IP (IPv4 e IPv6) e dos geradores de perguntas."""
import unittest

from services import ip_service


class IpServiceTests(unittest.TestCase):
    def test_network_id_ipv4(self):
        self.assertEqual(ip_service.calculate_network_id("192.168.1.130", 24), "192.168.1.0")

    def test_broadcast_ipv4(self):
        self.assertEqual(ip_service.calculate_broadcast("192.168.1.10", 24), "192.168.1.255")

    def test_same_ipv4_network(self):
        self.assertTrue(ip_service.same_ipv4_network("10.0.0.1", "10.0.0.254", 24))
        self.assertFalse(ip_service.same_ipv4_network("10.0.0.1", "10.0.1.1", 24))

    def test_ipv6_network_id(self):
        result = ip_service.calculate_ipv6_network_id("2001:db8::1", 64)
        self.assertEqual(result, "2001:db8::")

    def test_same_ipv6_network(self):
        self.assertTrue(ip_service.same_ipv6_network("2001:db8::1", "2001:db8::abcd", 64))

    def test_generated_questions_have_four_valid_options(self):
        for level in (1, 2, 3):
            question = ip_service.generate_ipv4_question(level)
            self.assertEqual(len(question["options"]), 4)
            self.assertTrue(0 <= question["correct_index"] < 4)
            self.assertEqual(question["level"], level)
        ipv6 = ip_service.generate_ipv6_question()
        self.assertEqual(len(ipv6["options"]), 4)
        self.assertTrue(0 <= ipv6["correct_index"] < 4)
        self.assertEqual(ipv6["level"], 4)


if __name__ == "__main__":
    unittest.main()
