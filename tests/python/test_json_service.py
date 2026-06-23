"""Teste unitário simples para leitura e escrita de JSON."""
import os
import tempfile
import unittest

from services.json_service import load, save


class JsonServiceTests(unittest.TestCase):
    def test_save_and_load_json(self):
        # O teste cria e apaga automaticamente o seu próprio ficheiro.
        with tempfile.TemporaryDirectory() as directory:
            filename = os.path.join(directory, "test.json")
            expected_data = {"nome": "teste", "valor": 10}
            save(filename, expected_data)
            self.assertEqual(load(filename, {}), expected_data)

    def test_load_creates_missing_file_with_default_value(self):
        with tempfile.TemporaryDirectory() as directory:
            filename = os.path.join(directory, "new.json")
            self.assertEqual(load(filename, []), [])
            self.assertTrue(os.path.exists(filename))


if __name__ == "__main__":
    unittest.main()
