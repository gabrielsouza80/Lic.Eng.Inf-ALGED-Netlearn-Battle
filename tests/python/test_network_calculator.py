"""Testes dos cálculos de endereçamento pedidos no enunciado."""
import unittest

from services.network_calculator import broadcast, network_id, same_network, subnet_count


class NetworkCalculatorTests(unittest.TestCase):
    def test_ipv4_network_id_and_broadcast(self):
        self.assertEqual(network_id("192.168.1.10/24"), "192.168.1.0")
        self.assertEqual(broadcast("192.168.1.10/24"), "192.168.1.255")

    def test_same_network_and_different_network(self):
        self.assertTrue(same_network("192.168.1.10", "192.168.1.200", 24))
        self.assertFalse(same_network("192.168.1.10", "192.168.2.10", 24))

    def test_ipv6_network_and_subnets(self):
        self.assertEqual(network_id("2001:db8:1::10/64"), "2001:db8:1::")
        self.assertIsNone(broadcast("2001:db8:1::10/64"))
        self.assertEqual(subnet_count(64, 68, version=6), 16)


if __name__ == "__main__":
    unittest.main()
