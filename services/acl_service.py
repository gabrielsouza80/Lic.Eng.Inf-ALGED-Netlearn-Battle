"""Motor simples de ACL (Access Control List).

Avalia se um pacote é permitido ou negado por um conjunto de regras e gera
perguntas de escolha múltipla para o nível 5. Os dados vêm de data/acls.json.
"""
import copy
import ipaddress
import random

from services.json_service import load

POINTS_CORRECT = 50
POINTS_WRONG = -25
TOPIC = "ACLs simples"


# ----------------------------------------------------------------------
# Leitura dos dados
# ----------------------------------------------------------------------
def _load_data():
    """Lê data/acls.json e devolve o dicionário com acls, packets e questions."""
    return load("acls.json", {"acls": [], "packets": [], "questions": []})


# ----------------------------------------------------------------------
# Lógica de correspondência
# ----------------------------------------------------------------------
def _ip_in(value, ip):
    """Devolve True se 'ip' pertence ao campo da regra ('any' ou um CIDR)."""
    if value == "any":
        return True
    # ip_network aceita "192.168.1.10/32" ou "192.168.1.0/24".
    network = ipaddress.ip_network(value, strict=False)
    return ipaddress.ip_address(ip) in network


def _protocol_match(rule_protocol, packet_protocol):
    """Protocolo igual, ou 'any'/'ip' que funcionam como coringa."""
    if rule_protocol in ("any", "ip"):
        return True
    return rule_protocol.lower() == str(packet_protocol).lower()


def _port_match(rule_port, packet_port):
    """Porta igual, ou 'any' que aceita qualquer porta."""
    if rule_port == "any":
        return True
    return int(rule_port) == int(packet_port)


def rule_matches_packet(rule, packet):
    """Devolve True se a regra corresponde ao pacote.

    Verifica protocolo, IP de origem, IP de destino e porta. Aceita 'any'.
    """
    return (_protocol_match(rule["protocol"], packet["protocol"])
            and _ip_in(rule["src"], packet["src_ip"])
            and _ip_in(rule["dst"], packet["dst_ip"])
            and _port_match(rule["port"], packet["port"]))


def evaluate_acl(rules, packet):
    """Percorre as regras por ordem e aplica a primeira que faz match.

    Devolve action ('permit'/'deny'), matched_rule_id e reason. Se nenhuma
    regra fizer match, devolve deny por padrão (deny implícito).
    """
    for rule in rules:
        if rule_matches_packet(rule, packet):
            return {
                "action": rule["action"],
                "matched_rule_id": rule["id"],
                "reason": f"Regra {rule['id']} fez match e diz {rule['action']}.",
            }
    return {
        "action": "deny",
        "matched_rule_id": None,
        "reason": "Nenhuma regra fez match: aplica-se o deny implícito.",
    }


# ----------------------------------------------------------------------
# Texto legível para as opções das perguntas
# ----------------------------------------------------------------------
def format_rule(rule):
    """Transforma uma regra num texto curto para mostrar na pergunta."""
    port = "qualquer porta" if rule["port"] == "any" else f"porta {rule['port']}"
    return (f"{rule['action']} {rule['protocol']} {rule['src']} -> "
            f"{rule['dst']} {port}")


def format_packet(packet):
    """Transforma um pacote num texto curto para mostrar na pergunta."""
    return (f"{packet['protocol']} de {packet['src_ip']} para "
            f"{packet['dst_ip']} porta {packet['port']}")


def _question(question_text, options, correct_index, question_type):
    """Cria o dicionário padrão de uma pergunta de nível 5."""
    return {
        "level": 5,
        "topic": TOPIC,
        "question": question_text,
        "options": options,
        "correct_index": correct_index,
        "points_correct": POINTS_CORRECT,
        "points_wrong": POINTS_WRONG,
        "question_type": question_type,
    }


# ----------------------------------------------------------------------
# Geradores de perguntas (nível 5)
# ----------------------------------------------------------------------
def generate_acl_permit_deny_question():
    """Dada uma ACL e um pacote, pergunta se o resultado é permit ou deny."""
    data = _load_data()
    acl = random.choice(data["acls"])
    packet = random.choice(data["packets"])
    result = evaluate_acl(acl["rules"], packet)

    rules_text = "; ".join(format_rule(rule) for rule in acl["rules"])
    question = (f"ACL '{acl['name']}': {rules_text}. "
                f"O pacote {format_packet(packet)} é permitido ou negado?")
    options = ["permit", "deny"]
    correct_index = options.index(result["action"])
    return _question(question, options, correct_index, "permit_deny")


def generate_acl_first_match_question():
    """Dada uma ACL e um pacote, pergunta qual foi a primeira regra que fez match."""
    data = _load_data()
    # Procura uma combinação que faça match numa regra (não no deny implícito).
    for _ in range(20):
        acl = random.choice(data["acls"])
        packet = random.choice(data["packets"])
        result = evaluate_acl(acl["rules"], packet)
        if result["matched_rule_id"] is not None:
            break

    rules_text = "; ".join(f"{r['id']}: {format_rule(r)}" for r in acl["rules"])
    question = (f"ACL '{acl['name']}': {rules_text}. "
                f"Qual é a PRIMEIRA regra que faz match com o pacote "
                f"{format_packet(packet)}?")
    options = [rule["id"] for rule in acl["rules"]]
    if "Nenhuma (deny implícito)" not in options:
        options.append("Nenhuma (deny implícito)")
    correct = result["matched_rule_id"] or "Nenhuma (deny implícito)"
    return _question(question, options, options.index(correct), "first_match")


def generate_acl_order_question():
    """Pergunta qual ordem de regras produz um determinado comportamento."""
    # Duas regras que entram em conflito: a ordem muda o resultado.
    permit_rule = {"id": "P", "action": "permit", "protocol": "tcp",
                   "src": "192.168.1.0/24", "dst": "10.0.0.10/32", "port": 80}
    deny_rule = {"id": "D", "action": "deny", "protocol": "tcp",
                 "src": "any", "dst": "10.0.0.10/32", "port": 80}
    packet = {"src_ip": "192.168.1.50", "dst_ip": "10.0.0.10",
              "protocol": "tcp", "port": 80}

    order_a = [permit_rule, deny_rule]
    order_b = [deny_rule, permit_rule]
    # Queremos a ordem que PERMITE o pacote.
    correct_order = order_a if evaluate_acl(order_a, packet)["action"] == "permit" else order_b

    def order_text(order):
        return " depois ".join(f"{format_rule(rule)}" for rule in order)

    options = [order_text(order_a), order_text(order_b)]
    question = (f"Quer permitir o pacote {format_packet(packet)}. "
                f"Qual ordem das regras produz 'permit'?")
    return _question(question, options, options.index(order_text(correct_order)),
                     "order")


def generate_acl_missing_ace_question():
    """Dada uma ACL incompleta, pergunta qual regra (ACE) falta."""
    data = _load_data()
    # Escolhe uma ACL com pelo menos 3 regras para a pergunta fazer sentido.
    candidates = [acl for acl in data["acls"] if len(acl["rules"]) >= 3]
    acl = random.choice(candidates or data["acls"])
    rules = copy.deepcopy(acl["rules"])
    missing = rules.pop(random.randrange(len(rules) - 1))  # não remove o deny final

    shown = "; ".join(format_rule(rule) for rule in rules)
    question = (f"A ACL '{acl['name']}' ficou incompleta: {shown}. "
                f"Qual regra (ACE) está em falta?")
    correct = format_rule(missing)
    # Distratores: regras de outras ACLs.
    distractors = []
    for other in data["acls"]:
        for rule in other["rules"]:
            text = format_rule(rule)
            if text != correct and text not in distractors:
                distractors.append(text)
    random.shuffle(distractors)
    options = [correct] + distractors[:3]
    random.shuffle(options)
    return _question(question, options, options.index(correct), "missing_ace")


def generate_acl_for_server_question():
    """Dado um servidor e serviços, pergunta qual ACL permite o acesso externo."""
    server = "192.168.1.10"
    question = (f"O servidor {server} oferece HTTP (porta 80) e HTTPS "
                f"(porta 443). Qual ACL permite o acesso externo a esses "
                f"serviços e nega o resto?")
    correct = (f"permit tcp any -> {server}/32 porta 80; "
               f"permit tcp any -> {server}/32 porta 443; "
               f"deny any any")
    distractors = [
        f"permit tcp any -> {server}/32 porta 22; deny any any",
        f"deny tcp any -> {server}/32 porta 80; permit any any",
        f"permit udp any -> {server}/32 porta 80; deny any any",
    ]
    options = [correct] + distractors
    random.shuffle(options)
    return _question(question, options, options.index(correct), "acl_for_server")


# Lista de geradores usada pelo GameService para o nível 5.
ACL_GENERATORS = [
    generate_acl_permit_deny_question,
    generate_acl_first_match_question,
    generate_acl_order_question,
    generate_acl_missing_ace_question,
    generate_acl_for_server_question,
]


def generate_acl_question():
    """Escolhe um dos geradores ACL ao acaso e devolve uma pergunta."""
    return random.choice(ACL_GENERATORS)()
