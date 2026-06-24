"""Avaliação simples de ACL: a primeira regra compatível decide o resultado."""
import random
import ipaddress
from services.json_service import load


def _ip_matches(rule_value, address):
    return rule_value == "any" or ipaddress.ip_address(address) in ipaddress.ip_network(rule_value, strict=False)


def rule_matches_packet(rule, packet):
    """Confirma protocolo, origem, destino e porta de uma regra ACL."""
    rule_protocol = rule.get("protocol", "any").lower()
    packet_protocol = packet.get("protocol", "").lower()
    protocol_ok = rule_protocol in ("any", "ip") or rule_protocol == packet_protocol
    port = rule.get("port", "any")
    port_ok = port == "any" or port == packet["port"]
    return protocol_ok and port_ok and _ip_matches(rule.get("src", "any"), packet["src_ip"]) and _ip_matches(rule.get("dst", "any"), packet["dst_ip"])


def evaluate_acl(rules, packet):
    """Percorre regras por ordem e aplica a primeira que faz match."""
    for rule in rules:
        if rule_matches_packet(rule, packet):
            return {"action": rule["action"], "matched_rule_id": rule["id"],
                    "reason": f"A regra {rule['id']} foi a primeira compatível."}
    return {"action": "deny", "matched_rule_id": None,
            "reason": "Nenhuma regra fez match; deny é aplicado por padrão."}


def _scenarios():
    return [item for item in load("acls.json", [])
            if isinstance(item, dict) and "rules" in item and "packet" in item]


def generate_acl_question():
    """Cria pergunta permit/deny a partir de um cenário guardado em acls.json."""
    scenarios = _scenarios()
    if not scenarios:
        return None
    scenario = random.choice(scenarios)
    result = evaluate_acl(scenario["rules"], scenario["packet"])
    options = ["permit", "deny"]
    return {"level": 5, "topic": "ACL simples",
            "question": scenario["question"], "options": options,
            "correct_index": options.index(result["action"]),
            "points_correct": 50, "points_wrong": -25,
            "question_type": "acl_permit_deny",
            "acl_reason": result["reason"]}


def _acl_question(text, options, correct, question_type):
    return {"level": 5, "topic": "ACL simples", "question": text,
            "options": options, "correct_index": options.index(correct),
            "points_correct": 50, "points_wrong": -25, "question_type": question_type}


def generate_acl_first_match_question(rules, packet):
    result = evaluate_acl(rules, packet)
    rule_ids = [r["id"] for r in rules]
    all_options = rule_ids + ["Nenhuma regra"]
    correct = result["matched_rule_id"] or "Nenhuma regra"
    return _acl_question("Qual foi a primeira regra ACL que fez match?", all_options, correct, "acl_first_match")


def generate_acl_order_question():
    correct = "deny SSH antes de permit geral"
    options = [
        "deny SSH antes de permit geral",
        "permit geral antes de deny SSH",
        "apenas permit SSH",
        "sem regras",
    ]
    random.shuffle(options)
    return _acl_question("Que ordem bloqueia SSH mas permite HTTP?", options, correct, "acl_order")


def generate_acl_missing_ace_question():
    correct = "permit tcp any 192.168.1.10/32 443"
    options = [
        "permit tcp any 192.168.1.10/32 443",
        "deny tcp any any 443",
        "permit udp any any 443",
        "permit tcp any any 22",
    ]
    random.shuffle(options)
    return _acl_question("Que ACE falta para permitir HTTPS ao servidor?", options, correct, "acl_missing_ace")


def generate_acl_for_server_question():
    correct = "permit tcp any 192.168.1.10/32 portas 80 e 443; deny restante"
    options = [
        "permit tcp any 192.168.1.10/32 portas 80 e 443; deny restante",
        "permit ip any any",
        "deny ip any any",
        "permit tcp any 192.168.1.10/32 porta 22",
    ]
    random.shuffle(options)
    return _acl_question("Qual ACL permite HTTP e HTTPS externos ao servidor 192.168.1.10?", options, correct, "acl_server")
