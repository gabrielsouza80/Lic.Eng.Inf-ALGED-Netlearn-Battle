"""[Secção 7] Repõe os dados criados pelos utilizadores para um estado vazio."""
import json
from pathlib import Path


DATA_DIR = Path(__file__).resolve().parent / "data"


def save_empty_file(filename, content):
    """Guarda uma estrutura JSON vazia com formatação simples."""
    path = DATA_DIR / filename
    path.write_text(json.dumps(content, indent=2), encoding="utf-8")


def reset_user_data():
    """Limpa contas, scores e histórico; não altera perguntas nem ACLs."""
    save_empty_file("users.json", [])
    save_empty_file("scores.json", {})
    save_empty_file("attempts.json", [])


if __name__ == "__main__":
    print("Este comando vai apagar contas, scores e tentativas guardadas.")
    confirmation = input("Escreva SIM para continuar: ").strip()
    if confirmation == "SIM":
        reset_user_data()
        print("Dados de utilizador repostos com sucesso.")
    else:
        print("Operação cancelada. Nenhum ficheiro foi alterado.")
