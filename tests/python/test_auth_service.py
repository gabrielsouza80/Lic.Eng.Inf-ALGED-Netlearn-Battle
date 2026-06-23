"""Testes unitários para registo, hash e login."""
import os
import tempfile
import unittest

from services.auth_service import AuthService
from services.json_service import load


class AuthServiceTests(unittest.TestCase):
    def test_register_saves_hash_and_login_works(self):
        with tempfile.TemporaryDirectory() as directory:
            filename = os.path.join(directory, "users.json")
            service = AuthService(filename)
            ok, _ = service.register("aluno_teste", "senha123")
            user = load(filename, [])[0]

            self.assertTrue(ok)
            self.assertNotIn("senha123", user.values())
            self.assertTrue(user["salt"])
            self.assertTrue(user["password_hash"])
            self.assertTrue(service.login("aluno_teste", "senha123"))
            self.assertFalse(service.login("aluno_teste", "senha_errada"))

    def test_register_rejects_invalid_and_duplicate_user(self):
        with tempfile.TemporaryDirectory() as directory:
            service = AuthService(os.path.join(directory, "users.json"))
            self.assertFalse(service.register("ab", "senha123")[0])
            self.assertFalse(service.register("nome invalido", "senha123")[0])
            self.assertFalse(service.register("aluno", "123")[0])
            self.assertTrue(service.register("Aluno", "senha123")[0])
            self.assertFalse(service.register("aluno", "senha123")[0])


if __name__ == "__main__":
    unittest.main()
