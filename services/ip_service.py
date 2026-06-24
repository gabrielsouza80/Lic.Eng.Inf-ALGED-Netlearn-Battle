"""Serviço académico para cálculos IPv4 e IPv6 com ipaddress."""
import ipaddress


def calculate_network_id(ip, prefix):
    return str(ipaddress.ip_network(f"{ip}/{prefix}", strict=False).network_address)


def calculate_broadcast(ip, prefix):
    return str(ipaddress.ip_network(f"{ip}/{prefix}", strict=False).broadcast_address)


def same_ipv4_network(ip1, ip2, prefix):
    return calculate_network_id(ip1, prefix) == calculate_network_id(ip2, prefix)


def calculate_ipv6_network_id(ipv6, prefix):
    return str(ipaddress.ip_network(f"{ipv6}/{prefix}", strict=False).network_address)


def calculate_ipv6_last_address(ipv6, prefix):
    return str(ipaddress.ip_network(f"{ipv6}/{prefix}", strict=False).broadcast_address)


def same_ipv6_network(ip1, ip2, prefix):
    return calculate_ipv6_network_id(ip1, prefix) == calculate_ipv6_network_id(ip2, prefix)


def calculate_ipv6_subnets(network, new_prefix):
    return [str(item) for item in list(ipaddress.ip_network(network, strict=False).subnets(new_prefix=new_prefix))[:4]]
