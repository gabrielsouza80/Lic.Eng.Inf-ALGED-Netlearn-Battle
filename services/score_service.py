"""Leitura, atualização e ranking de pontuações em scores.json."""
from services.json_service import load, save
class ScoreService:
    def get_score(self, username): return load("scores.json", {}).get(username, 0)
    def add_points(self, username, points):
        # Cada utilizador tem apenas um score atual no ficheiro JSON.
        scores = load("scores.json", {}); scores[username] = scores.get(username, 0) + points; save("scores.json", scores); return scores[username]
    def top_five(self):
        # Ordena do maior score para o menor e devolve apenas cinco resultados.
        pairs = sorted(load("scores.json", {}).items(), key=lambda item: (-item[1], item[0].lower()))
        return [{"username": name, "score": score} for name, score in pairs[:5]]
