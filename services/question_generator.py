"""Gera perguntas simples de redes com respostas calculadas pelo projeto."""
import random

from services.network_calculator import broadcast, network_id, same_network, subnet_count


POINTS = {1: (10, -5), 2: (20, -10), 3: (30, -15), 4: (40, -20)}


def _question(level, topic, text, options, correct, question_type="calculation"):
    """Constrói o dicionário comum das perguntas de escolha múltipla."""
    correct_points, wrong_points = POINTS[level]
    return {"level": level, "topic": topic, "question": text,
            "options": options, "correct_index": options.index(correct),
            "points_correct": correct_points, "points_wrong": wrong_points,
            "question_type": question_type}


def _with_options(correct, wrong):
    """Mistura uma resposta correta com alternativas, sem respostas repetidas."""
    options = list(dict.fromkeys([correct] + wrong))[:4]
    random.shuffle(options)
    return options


def generate_network_question(level):
    """Gera uma pergunta IPv4/IPv6 adequada ao nível escolhido."""
    if level == 1:
        ip, prefix = random.choice([("10.20.30.40", 8), ("172.16.5.10", 16), ("192.168.1.10", 24)])
        kind = random.choice(["network", "broadcast", "same"])
        topic = "IPv4 básico"
    elif level == 2:
        ip, prefix = random.choice([("192.168.1.70", 25), ("192.168.1.70", 26), ("192.168.1.70", 27)])
        kind = random.choice(["network", "broadcast", "same"])
        topic = "Sub-redes IPv4"
    elif level == 3:
        ip, prefix = random.choice([("10.1.3.10", 21), ("172.16.5.10", 22), ("10.1.3.10", 23)])
        kind = random.choice(["network", "broadcast", "same"])
        topic = "Super-redes IPv4"
    elif level == 4:
        return _ipv6_question()
    else:
        return None

    address = f"{ip}/{prefix}"
    if kind == "network":
        correct = network_id(address)
        return _question(level, topic, f"Qual é o Network ID de {address}?",
                         _with_options(correct, [ip, "0.0.0.0", "255.255.255.255"]), correct, "network_id")
    if kind == "broadcast":
        correct = broadcast(address)
        return _question(level, topic, f"Qual é o broadcast de {address}?",
                         _with_options(correct, [network_id(address), ip, "255.255.255.255"]), correct, "broadcast")

    other = ip.rsplit(".", 1)[0] + ".200"
    correct = "Sim" if same_network(ip, other, prefix) else "Não"
    return _question(level, topic, f"Os IPs {ip} e {other} pertencem à mesma rede /{prefix}?",
                     ["Sim", "Não"], correct, "same_network")


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
