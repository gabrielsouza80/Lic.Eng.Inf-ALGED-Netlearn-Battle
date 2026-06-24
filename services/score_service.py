"""[Secções 27 e 28] Atualização de score e ranking em scores.json."""
from services.json_service import load, save


class ScoreService:
    def __init__(self, filename="scores.json"):
        # Nos testes, filename aponta para um ficheiro temporário.
        self.filename = filename

    def get_score(self, username):
        # Um score deve ser um número. Esta verificação evita que um JSON editado
        # manualmente impeça o dashboard de abrir.
        scores = load(self.filename, {})
        if not isinstance(scores, dict):
            return 0
        score = scores.get(username, 0)
        return score if isinstance(score, (int, float)) and not isinstance(score, bool) else 0

    def add_points(self, username, points):
        # [Secção 27] Cada utilizador tem apenas um score atual no JSON.
        scores = load(self.filename, {})
        if not isinstance(scores, dict):
            # Não substituímos silenciosamente um JSON de formato errado.
            raise ValueError("scores.json deve conter um objeto com pontuações.")
        scores[username] = self.get_score(username) + points
        save(self.filename, scores)
        return scores[username]

    def top_five(self):
        # [Secção 28] Ordena do maior score para o menor e devolve Top 5.
        raw_scores = load(self.filename, {})
        if not isinstance(raw_scores, dict):
            return []
        # Não mostramos valores inválidos no ranking. Isto protege a página caso
        # alguém edite scores.json e escreva texto em vez de um número.
        pairs = [(name, score) for name, score in raw_scores.items()
                 if isinstance(name, str) and isinstance(score, (int, float))
                 and not isinstance(score, bool)]
        pairs.sort(key=lambda item: (-item[1], item[0].lower()))
        return [{"username": name, "score": score} for name, score in pairs[:5]]
