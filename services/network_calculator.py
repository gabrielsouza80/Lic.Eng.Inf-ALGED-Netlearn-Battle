"""Cálculos simples de IPv4 e IPv6 usados nas perguntas do jogo."""
import ipaddress


def network_id(address_with_prefix):
    """Devolve o endereço da rede de um IPv4 ou IPv6 com prefixo."""
    return str(ipaddress.ip_interface(address_with_prefix).network.network_address)


def broadcast(address_with_prefix):
    """Devolve o broadcast de uma rede IPv4. IPv6 não possui broadcast."""
    interface = ipaddress.ip_interface(address_with_prefix)
    if interface.version != 4:
        return None
    return str(interface.network.broadcast_address)


def same_network(first_address, second_address, prefix):
    """Verifica se dois endereços pertencem à mesma rede com o prefixo dado."""
    first = ipaddress.ip_interface(f"{first_address}/{prefix}").network
    second = ipaddress.ip_interface(f"{second_address}/{prefix}").network
    return first == second


def subnet_count(prefix, new_prefix, version=4):
    """Calcula quantas sub-redes surgem ao aumentar um prefixo."""
    max_prefix = 32 if version == 4 else 128
    if not 0 <= prefix <= new_prefix <= max_prefix:
        raise ValueError("Prefixos inválidos para o cálculo de sub-redes.")
    return 2 ** (new_prefix - prefix)
