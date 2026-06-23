"""[Secções 27 e 28] Atualização de score e ranking em scores.json."""
from services.json_service import load, save


class ScoreService:
    def __init__(self, filename="scores.json"):
        # Nos testes, filename aponta para um ficheiro temporário.
        self.filename = filename

    def get_score(self, username):
        return load(self.filename, {}).get(username, 0)

    def add_points(self, username, points):
        # [Secção 27] Cada utilizador tem apenas um score atual no JSON.
        scores = load(self.filename, {})
        scores[username] = scores.get(username, 0) + points
        save(self.filename, scores)
        return scores[username]

    def top_five(self):
        # [Secção 28] Ordena do maior score para o menor e devolve Top 5.
        pairs = sorted(load(self.filename, {}).items(), key=lambda item: (-item[1], item[0].lower()))
        return [{"username": name, "score": score} for name, score in pairs[:5]]
