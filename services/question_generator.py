"""Gera perguntas simples de redes com respostas calculadas pelo projeto."""
import random
import ipaddress

from services.network_calculator import broadcast, network_id, same_network, subnet_count


POINTS = {1: (10, -5), 2: (20, -10), 3: (30, -15), 4: (40, -20)}

PRIVATE_RANGES = {
    1: ["10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16"],
    2: ["10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16"],
    3: ["10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16"],
}

PREFIXES = {
    1: [8, 16, 24],
    2: [25, 26, 27],
    3: [21, 22, 23],
}


def _random_ip_in_range(net_str):
    net = ipaddress.ip_network(net_str, strict=False)
    network_int = int(net.network_address)
    broadcast_int = int(net.broadcast_address)
    host_int = random.randint(network_int + 1, broadcast_int - 1)
    return str(ipaddress.IPv4Address(host_int))


def _question(level, topic, text, options, correct, question_type="calculation"):
    correct_points, wrong_points = POINTS[level]
    return {"level": level, "topic": topic, "question": text,
            "options": options, "correct_index": options.index(correct),
            "points_correct": correct_points, "points_wrong": wrong_points,
            "question_type": question_type}


def _with_options(correct, wrong):
    options = list(dict.fromkeys([correct] + wrong))[:4]
    random.shuffle(options)
    return options


def _network_alternatives(net):
    step = 1 << (32 - net.prefixlen)
    base = int(net.network_address)
    alternatives = []
    for offset in [1, -1, 2, -2, 3, -3]:
        alt_int = base + offset * step
        if 0 <= alt_int < (1 << 32) and alt_int != base:
            alternatives.append(str(ipaddress.IPv4Address(alt_int)))
        if len(alternatives) >= 3:
            break
    while len(alternatives) < 3:
        alt = str(ipaddress.IPv4Address(random.randint(1, (1 << 32) - 2)))
        if alt not in alternatives:
            alternatives.append(alt)
    return alternatives[:3]


def _broadcast_alternatives(net):
    step = 1 << (32 - net.prefixlen)
    base = int(net.network_address)
    alternatives = []
    for offset in [1, -1, 2, -2]:
        alt_net = base + offset * step
        if 0 <= alt_net < (1 << 32) and alt_net != base:
            alt_bc = alt_net + step - 1
            alternatives.append(str(ipaddress.IPv4Address(alt_bc)))
    while len(alternatives) < 3:
        alt = str(ipaddress.IPv4Address(random.randint(1, (1 << 32) - 2)))
        if alt not in alternatives:
            alternatives.append(alt)
    return alternatives[:3]


def generate_network_question(level):
    if level == 4:
        return _ipv6_question()
    if level not in PRIVATE_RANGES:
        return None

    base_net = random.choice(PRIVATE_RANGES[level])
    prefix = random.choice(PREFIXES[level])
    kind = random.choice(["network", "broadcast", "same"])

    topic = {1: "IPv4 básico", 2: "Sub-redes IPv4", 3: "Super-redes IPv4"}[level]
    ip = _random_ip_in_range(base_net)
    address = f"{ip}/{prefix}"
    net = ipaddress.ip_network(address, strict=False)

    if kind == "network":
        correct = network_id(address)
        alternatives = _network_alternatives(net)
        return _question(level, topic, f"Qual é o Network ID de {address}?",
                         _with_options(correct, alternatives), correct, "network_id")

    if kind == "broadcast":
        correct = broadcast(address)
        return _question(level, topic, f"Qual é o broadcast de {address}?",
                         _with_options(correct, [network_id(address)] + _broadcast_alternatives(net)),
                         correct, "broadcast")

    net_int = int(net.network_address)
    broadcast_int = int(net.broadcast_address)
    if random.choice([True, False]):
        other_int = random.randint(net_int + 1, broadcast_int - 1)
        other = str(ipaddress.IPv4Address(other_int))
        correct_text = "Sim"
    else:
        step = 1 << (32 - prefix)
        if random.random() < 0.5:
            offset = random.choice([1, -1, 2, -2])
            other_net_int = net_int + offset * step
            if other_net_int < 0 or other_net_int >= (1 << 32):
                other_net_int = net_int - step
            other_int = random.randint(other_net_int + 1, other_net_int + step - 1)
            other = str(ipaddress.IPv4Address(other_int))
        else:
            other_range = random.choice([r for r in PRIVATE_RANGES[level] if r != base_net])
            other = _random_ip_in_range(other_range)
        correct_text = "Não"
    return _question(level, topic, f"Os IPs {ip} e {other} pertencem à mesma rede /{prefix}?",
                     ["Sim", "Não"], correct_text, "same_network")


def _ipv6_question():
    kind = random.choice(["network", "same", "subnets", "broadcast"])
    if kind == "network":
        correct = network_id("2001:db8:1::10/64")
        return _question(4, "IPv6", "Qual é o Network ID de 2001:db8:1::10/64?",
                         _with_options(correct, ["2001:db8::", "2001:db8:1::10", "ffff:ffff::"]), correct)
    if kind == "same":
        correct = "Sim" if same_network("2001:db8:1::1", "2001:db8:1::20", 64) else "Não"
        return _question(4, "IPv6", "2001:db8:1::1 e 2001:db8:1::20 pertencem à mesma rede /64?", ["Sim", "Não"], correct)
    if kind == "subnets":
        correct = str(subnet_count(64, 68, version=6))
        return _question(4, "IPv6", "Quantas sub-redes /68 existem dentro de uma rede IPv6 /64?", ["2", "4", "16", "64"], correct)
    return _question(4, "IPv6", "IPv6 possui endereço de broadcast?", ["Sim", "Não"], "Não")
