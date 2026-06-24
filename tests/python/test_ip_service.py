"""Testes pedidos para o motor IPv4 e IPv6."""
import unittest
from services.ip_service import calculate_network_id, calculate_broadcast, same_ipv4_network, calculate_ipv6_network_id, same_ipv6_network


class IpServiceTests(unittest.TestCase):
    def test_ipv4(self):
        self.assertEqual(calculate_network_id("192.168.1.10", 24), "192.168.1.0")
        self.assertEqual(calculate_broadcast("192.168.1.10", 24), "192.168.1.255")
        self.assertTrue(same_ipv4_network("10.0.0.1", "10.0.0.200", 24))

    def test_ipv6(self):
        self.assertEqual(calculate_ipv6_network_id("2001:db8:1::10", 64), "2001:db8:1::")
        self.assertTrue(same_ipv6_network("2001:db8:1::1", "2001:db8:1::2", 64))


if __name__ == "__main__":
    unittest.main()
