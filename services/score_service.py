"""Leitura, atualização e ranking de pontuações em scores.json."""
from services.json_service import load, save


class ScoreService:
    def __init__(self, filename="scores.json"):
        # Nos testes, filename aponta para um ficheiro temporário.
        self.filename = filename

    def get_score(self, username):
        return load(self.filename, {}).get(username, 0)

    def add_points(self, username, points):
        # Cada utilizador tem apenas um score atual no ficheiro JSON.
        scores = load(self.filename, {})
        scores[username] = scores.get(username, 0) + points
        save(self.filename, scores)
        return scores[username]

    def top_five(self):
        # Ordena do maior score para o menor e devolve apenas cinco resultados.
        pairs = sorted(load(self.filename, {}).items(), key=lambda item: (-item[1], item[0].lower()))
        return [{"username": name, "score": score} for name, score in pairs[:5]]
