"""[Secções 6 e 7] Leitura e escrita dos ficheiros JSON do projeto."""
import json
import os
import time
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# NETLEARN_DATA_DIR permite mudar toda a pasta data apenas se for necessário.
DATA_DIR = os.environ.get("NETLEARN_DATA_DIR", os.path.join(ROOT_DIR, "data"))


def file_path(filename):
    """Aceita um ficheiro da pasta data ou um caminho temporário de teste."""
    return filename if os.path.isabs(filename) else os.path.join(DATA_DIR, filename)


def load(filename, default):
    """[Secção 6] Lê JSON; se não existir, cria o ficheiro com default."""
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
    """[Secção 6] Guarda dados no ficheiro JSON indicado."""
    path = file_path(filename)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    temporary = path + ".tmp"
    with open(temporary, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)
    # A substituição é atómica. No Windows, antivírus ou indexação podem bloquear o
    # ficheiro por alguns milissegundos; repetimos poucas vezes para evitar falhas.
    for attempt in range(5):
        try:
            os.replace(temporary, path)
            return
        except PermissionError:
            if attempt == 4:
                raise
            time.sleep(0.05)
