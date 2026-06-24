"""Avaliação simples de ACL: a primeira regra compatível decide o resultado."""
import ipaddress


def _ip_matches(rule_value, address):
    return rule_value == "any" or ipaddress.ip_address(address) in ipaddress.ip_network(rule_value, strict=False)


def rule_matches_packet(rule, packet):
    """Confirma protocolo, origem, destino e porta de uma regra ACL."""
    protocol_ok = rule.get("protocol", "any") in ("any", packet["protocol"])
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
