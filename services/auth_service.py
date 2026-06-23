"""Registo e login de utilizadores guardados em users.json."""
import hashlib
import secrets

from services.json_service import load, save


class AuthService:
    def _hash_password(self, password, salt):
        # O salt torna o hash diferente mesmo quando duas passwords são iguais.
        return hashlib.sha256((salt + password).encode("utf-8")).hexdigest()

    def register(self, username, password):
        if len(username) < 3 or not username.replace("_", "").isalnum():
            return False, "O utilizador deve ter pelo menos 3 caracteres alfanuméricos."
        if len(password) < 4:
            return False, "A password deve ter pelo menos 4 caracteres."
        users = load("users.json", [])
        if any(user["username"].lower() == username.lower() for user in users):
            return False, "Esse utilizador já existe."
        salt = secrets.token_hex(16)
        # A password original nunca é guardada no ficheiro JSON.
        users.append({"username": username, "salt": salt,
                      "password_hash": self._hash_password(password, salt)})
        save("users.json", users)
        return True, "Registo efetuado. Já pode fazer login."

    def login(self, username, password):
        for user in load("users.json", []):
            if user["username"] == username:
                received_hash = self._hash_password(password, user["salt"])
                return secrets.compare_digest(received_hash, user["password_hash"])
        return False
