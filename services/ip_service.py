"""Motor de cálculo de redes IPv4 e IPv6.

Usa apenas a biblioteca padrão ``ipaddress``. As funções são simples e servem
para corrigir respostas e para gerar perguntas de escolha múltipla.
"""
import ipaddress
import random

# Pontuação por nível: nível -> (pontos certo, pontos errado).
LEVEL_POINTS = {
    1: (10, -5),
    2: (20, -10),
    3: (30, -15),
    4: (40, -20),
}

# Prefixos usados em cada nível IPv4.
LEVEL_PREFIXES = {
    1: [8, 16, 24],
    2: [25, 26, 27],
    3: [21, 22, 23],
}

LEVEL_TOPIC = {
    1: "IPv4 básico",
    2: "Sub-redes IPv4",
    3: "Super-redes IPv4",
    4: "IPv6 simples",
}


# ----------------------------------------------------------------------
# Funções IPv4
# ----------------------------------------------------------------------
def calculate_network_id(ip, prefix):
    """Devolve o Network ID (endereço de rede) de um IP com um prefixo."""
    # strict=False permite usar um IP de host e não só o endereço de rede.
    network = ipaddress.ip_network(f"{ip}/{prefix}", strict=False)
    return str(network.network_address)


def calculate_broadcast(ip, prefix):
    """Devolve o endereço de broadcast de um IP com um prefixo."""
    network = ipaddress.ip_network(f"{ip}/{prefix}", strict=False)
    return str(network.broadcast_address)


def same_ipv4_network(ip1, ip2, prefix):
    """Devolve True se os dois IPs estiverem no mesmo segmento de rede."""
    network1 = ipaddress.ip_network(f"{ip1}/{prefix}", strict=False)
    network2 = ipaddress.ip_network(f"{ip2}/{prefix}", strict=False)
    return network1.network_address == network2.network_address


# ----------------------------------------------------------------------
# Funções IPv6
# ----------------------------------------------------------------------
def calculate_ipv6_network_id(ipv6, prefix):
    """Devolve o Network ID (endereço de rede) de um endereço IPv6."""
    network = ipaddress.ip_network(f"{ipv6}/{prefix}", strict=False)
    return str(network.network_address)


def calculate_ipv6_last_address(ipv6, prefix):
    """Devolve o último endereço da sub-rede IPv6.

    O IPv6 não usa broadcast como o IPv4. Aqui calculamos o último endereço da
    sub-rede e na interface chamamos-lhe "endereço final da sub-rede IPv6".
    """
    network = ipaddress.ip_network(f"{ipv6}/{prefix}", strict=False)
    return str(network.broadcast_address)


def same_ipv6_network(ip1, ip2, prefix):
    """Devolve True se os dois IPv6 estiverem no mesmo segmento."""
    network1 = ipaddress.ip_network(f"{ip1}/{prefix}", strict=False)
    network2 = ipaddress.ip_network(f"{ip2}/{prefix}", strict=False)
    return network1.network_address == network2.network_address


def calculate_ipv6_subnets(network, new_prefix):
    """Gera algumas sub-redes IPv6 a partir de uma rede e um novo prefixo.

    Devolve no máximo 4 sub-redes para manter a lista curta.
    """
    base = ipaddress.ip_network(network, strict=False)
    subnets = []
    for index, subnet in enumerate(base.subnets(new_prefix=new_prefix)):
        if index >= 4:
            break
        subnets.append(str(subnet))
    return subnets


# ----------------------------------------------------------------------
# Geradores de IPs aleatórios (ajudam a criar perguntas)
# ----------------------------------------------------------------------
def _random_ipv4():
    """Gera um IPv4 privado aleatório simples para usar nas perguntas."""
    return f"192.168.{random.randint(0, 255)}.{random.randint(1, 254)}"


def _random_ipv6():
    """Gera um IPv6 aleatório simples dentro de 2001:db8::/32."""
    blocks = [format(random.randint(0, 0xFFFF), "x") for _ in range(2)]
    return "2001:db8:" + ":".join(blocks) + "::" + format(random.randint(1, 0xFFFF), "x")


def _build_options(correct_value, wrong_values):
    """Cria 4 opções com a resposta correta numa posição aleatória.

    Devolve (options, correct_index). Garante 4 opções sem repetições.
    """
    options = [correct_value]
    for wrong in wrong_values:
        if wrong not in options:
            options.append(wrong)
        if len(options) == 4:
            break
    # Se faltarem opções (valores repetidos), completa com texto simples.
    while len(options) < 4:
        options.append(f"opção {len(options)}")
    random.shuffle(options)
    return options, options.index(correct_value)


# ----------------------------------------------------------------------
# Geração de perguntas IPv4 (níveis 1, 2 e 3)
# ----------------------------------------------------------------------
def generate_ipv4_question(level):
    """Gera uma pergunta IPv4 de escolha múltipla para o nível indicado.

    Tipos de pergunta: Network ID, Broadcast e "mesmo segmento".
    """
    if level not in LEVEL_PREFIXES:
        raise ValueError("Nível IPv4 inválido. Use 1, 2 ou 3.")

    prefix = random.choice(LEVEL_PREFIXES[level])
    points_correct, points_wrong = LEVEL_POINTS[level]
    topic = LEVEL_TOPIC[level]
    question_type = random.choice(["network_id", "broadcast", "same_network"])
    ip = _random_ipv4()

    if question_type == "network_id":
        correct = calculate_network_id(ip, prefix)
        wrongs = [calculate_broadcast(ip, prefix),
                  calculate_network_id(_random_ipv4(), prefix),
                  calculate_network_id(_random_ipv4(), prefix)]
        question = f"Qual é o Network ID de {ip}/{prefix}?"
        options, correct_index = _build_options(correct, wrongs)

    elif question_type == "broadcast":
        correct = calculate_broadcast(ip, prefix)
        wrongs = [calculate_network_id(ip, prefix),
                  calculate_broadcast(_random_ipv4(), prefix),
                  calculate_broadcast(_random_ipv4(), prefix)]
        question = f"Qual é o broadcast de {ip}/{prefix}?"
        options, correct_index = _build_options(correct, wrongs)

    else:  # same_network
        ip2 = _random_ipv4()
        same = same_ipv4_network(ip, ip2, prefix)
        correct = "Sim, mesmo segmento" if same else "Não, segmentos diferentes"
        wrongs = ["Não, segmentos diferentes" if same else "Sim, mesmo segmento"]
        question = (f"Os endereços {ip}/{prefix} e {ip2}/{prefix} "
                    f"pertencem ao mesmo segmento?")
        options, correct_index = _build_options(correct, wrongs)

    return {
        "level": level,
        "topic": topic,
        "question": question,
        "options": options,
        "correct_index": correct_index,
        "points_correct": points_correct,
        "points_wrong": points_wrong,
        "question_type": question_type,
    }


# ----------------------------------------------------------------------
# Geração de perguntas IPv6 (nível 4)
# ----------------------------------------------------------------------
def generate_ipv6_question():
    """Gera uma pergunta IPv6 de escolha múltipla (nível 4)."""
    points_correct, points_wrong = LEVEL_POINTS[4]
    topic = LEVEL_TOPIC[4]
    prefix = random.choice([48, 56, 64])
    question_type = random.choice(
        ["network_id", "last_address", "same_network", "subnet"])
    ipv6 = _random_ipv6()

    if question_type == "network_id":
        correct = calculate_ipv6_network_id(ipv6, prefix)
        wrongs = [calculate_ipv6_last_address(ipv6, prefix),
                  calculate_ipv6_network_id(_random_ipv6(), prefix),
                  calculate_ipv6_network_id(_random_ipv6(), prefix)]
        question = f"Qual é o Network ID de {ipv6}/{prefix}?"
        options, correct_index = _build_options(correct, wrongs)

    elif question_type == "last_address":
        correct = calculate_ipv6_last_address(ipv6, prefix)
        wrongs = [calculate_ipv6_network_id(ipv6, prefix),
                  calculate_ipv6_last_address(_random_ipv6(), prefix),
                  calculate_ipv6_last_address(_random_ipv6(), prefix)]
        question = f"Qual é o endereço final da sub-rede IPv6 {ipv6}/{prefix}?"
        options, correct_index = _build_options(correct, wrongs)

    elif question_type == "same_network":
        ip2 = _random_ipv6()
        same = same_ipv6_network(ipv6, ip2, prefix)
        correct = "Sim, mesmo segmento" if same else "Não, segmentos diferentes"
        wrongs = ["Não, segmentos diferentes" if same else "Sim, mesmo segmento"]
        question = (f"Os endereços IPv6 {ipv6}/{prefix} e {ip2}/{prefix} "
                    f"estão no mesmo segmento?")
        options, correct_index = _build_options(correct, wrongs)

    else:  # subnet
        base = calculate_ipv6_network_id(ipv6, prefix)
        new_prefix = prefix + 4
        subnets = calculate_ipv6_subnets(f"{base}/{prefix}", new_prefix)
        correct = subnets[0]
        wrongs = subnets[1:]
        question = (f"Qual é a primeira sub-rede /{new_prefix} da rede "
                    f"{base}/{prefix}?")
        options, correct_index = _build_options(correct, wrongs)

    return {
        "level": 4,
        "topic": topic,
        "question": question,
        "options": options,
        "correct_index": correct_index,
        "points_correct": points_correct,
        "points_wrong": points_wrong,
        "question_type": question_type,
    }
