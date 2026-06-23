"""Funções pequenas para ler e guardar os ficheiros JSON do projeto."""
import json
import os
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT_DIR, "data")


def file_path(filename):
    """Aceita um ficheiro da pasta data ou um caminho temporário de teste."""
    return filename if os.path.isabs(filename) else os.path.join(DATA_DIR, filename)


def load(filename, default):
    """Lê um JSON. Se ainda não existir, cria-o com o valor default."""
    path = file_path(filename)
    if not os.path.exists(path):
        save(filename, default)
        return default
    try:
        with open(path, encoding="utf-8") as file:
            return json.load(file)
    except (json.JSONDecodeError, OSError):
        raise ValueError(f"O ficheiro '{filename}' não contém JSON válido.")


def save(filename, data):
    """Guarda os dados recebidos no ficheiro JSON indicado."""
    path = file_path(filename)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    temporary = path + ".tmp"
    with open(temporary, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)
    os.replace(temporary, path)  # Evita JSON parcial se o programa for interrompido.
