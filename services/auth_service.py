"""Registo e login de utilizadores guardados em users.json."""
import hashlib
import secrets

from services.json_service import load, save


class AuthService:
    def __init__(self, filename="users.json"):
        # Nos testes, filename aponta para um ficheiro temporário.
        self.filename = filename

    def _hash_password(self, password, salt):
        # O salt torna o hash diferente mesmo quando duas passwords são iguais.
        return hashlib.sha256((salt + password).encode("utf-8")).hexdigest()

    def register(self, username, password):
        if len(username) < 3 or not username.replace("_", "").isalnum():
            return False, "O utilizador deve ter pelo menos 3 caracteres alfanuméricos."
        if len(password) < 4:
            return False, "A password deve ter pelo menos 4 caracteres."
        users = load(self.filename, [])
        if any(user["username"].lower() == username.lower() for user in users):
            return False, "Esse utilizador já existe."
        salt = secrets.token_hex(16)
        # A password original nunca é guardada no ficheiro JSON.
        users.append({"username": username, "salt": salt,
                      "password_hash": self._hash_password(password, salt)})
        save(self.filename, users)
        return True, "Registo efetuado. Já pode fazer login."

    def login(self, username, password):
        for user in load(self.filename, []):
            if user["username"] == username:
                received_hash = self._hash_password(password, user["salt"])
                return secrets.compare_digest(received_hash, user["password_hash"])
        return False
