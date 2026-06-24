"""Testes dos cálculos de endereçamento pedidos no enunciado."""
import unittest

from services.network_calculator import broadcast, network_id, same_network, subnet_count


class NetworkCalculatorTests(unittest.TestCase):
    def test_ipv4_network_id_and_broadcast(self):
        self.assertEqual(network_id("192.168.1.10/24"), "192.168.1.0")
        self.assertEqual(broadcast("192.168.1.10/24"), "192.168.1.255")

    def test_same_network_true(self):
        self.assertTrue(same_network("192.168.1.10", "192.168.1.200", 24))
        self.assertTrue(same_network("10.0.0.1", "10.0.0.254", 24))
        self.assertTrue(same_network("172.16.5.10", "172.16.5.200", 16))

    def test_same_network_false(self):
        self.assertFalse(same_network("192.168.1.10", "192.168.2.10", 24))
        self.assertFalse(same_network("10.0.0.1", "10.0.1.1", 24))
        self.assertFalse(same_network("172.16.5.10", "172.17.5.10", 16))

    def test_ipv6_network_id_and_same_network(self):
        self.assertEqual(network_id("2001:db8:1::10/64"), "2001:db8:1::")
        self.assertTrue(same_network("2001:db8:1::1", "2001:db8:1::20", 64))

    def test_ipv6_broadcast_is_none(self):
        self.assertIsNone(broadcast("2001:db8:1::10/64"))

    def test_subnet_count(self):
        self.assertEqual(subnet_count(64, 68, version=6), 16)
        self.assertEqual(subnet_count(24, 28), 16)


if __name__ == "__main__":
    unittest.main()
