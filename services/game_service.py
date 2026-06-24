"""Regras do jogo: perguntas (fixas + geradas), sessões, tentativas e pontuação."""
import random
import time
import uuid

from services import acl_service, ip_service
from services.json_service import load, save
from services.score_service import ScoreService
from structures.queue import Queue
from structures.stack import Stack

# Tamanho padrão de uma sessão de jogo (Queue de perguntas).
SESSION_SIZE = 5


class GameService:
    def __init__(self):
        self.scores = ScoreService()

    # ------------------------------------------------------------------
    # Histórico
    # ------------------------------------------------------------------
    def history_for(self, username):
        """Devolve as tentativas de um utilizador."""
        return [attempt for attempt in load("attempts.json", [])
                if attempt["username"] == username]

    def recent_attempts(self, limit=20):
        """Devolve as últimas tentativas de todos os alunos para o professor."""
        return list(reversed(load("attempts.json", [])[-limit:]))

    # ------------------------------------------------------------------
    # Geração de perguntas
    # ------------------------------------------------------------------
    def _fixed_questions(self, level):
        """Lê as perguntas fixas em JSON para o nível indicado."""
        if level == 5:
            fixed = load("acls.json", {}).get("questions", [])
        else:
            fixed = load("questions.json", [])
        return [question for question in fixed if question.get("level") == level]

    def _generate_question(self, level):
        """Gera automaticamente uma pergunta de acordo com o nível."""
        if level in (1, 2, 3):
            return ip_service.generate_ipv4_question(level)
        if level == 4:
            return ip_service.generate_ipv6_question()
        if level == 5:
            return acl_service.generate_acl_question()
        return None

    def create_question(self, level):
        """Devolve uma única pergunta do nível (modo misto fixo/gerado).

        Usa uma Queue (FIFO) só para demonstrar a estrutura: a primeira
        pergunta colocada é a primeira a sair.
        """
        queue = Queue()
        for question in self.build_session_questions(level, count=1):
            queue.enqueue(question)
        return queue.dequeue()

    def build_session_questions(self, level, count=SESSION_SIZE):
        """Cria a lista de perguntas de uma sessão de jogo.

        Modo misto: usa algumas perguntas fixas do JSON (se existirem) e
        completa o resto com perguntas geradas automaticamente.
        """
        if self._generate_question(level) is None and not self._fixed_questions(level):
            return []

        questions = []
        fixed = self._fixed_questions(level)
        random.shuffle(fixed)
        # No máximo 2 perguntas fixas para manter variedade com as geradas.
        for question in fixed[:2]:
            questions.append(question)
        while len(questions) < count:
            generated = self._generate_question(level)
            if generated is None:
                break
            questions.append(generated)
        return questions[:count]

    # ------------------------------------------------------------------
    # Sessão de jogo (Queue real)
    # ------------------------------------------------------------------
    def new_session_id(self):
        """Cria um identificador curto e único para uma sessão."""
        return uuid.uuid4().hex[:8]

    def grade_answer(self, username, question, selected_index, started_at, session_id):
        """Corrige uma resposta, atualiza o score e devolve a tentativa.

        A tentativa ainda NÃO é gravada em attempts.json; isso acontece no fim
        da sessão (a partir da Stack).
        """
        options = question["options"]
        valid_answer = 0 <= selected_index < len(options)
        correct_index = question["correct_index"]
        is_correct = valid_answer and selected_index == correct_index
        points = question["points_correct"] if is_correct else question["points_wrong"]
        selected_answer = options[selected_index] if valid_answer else "Sem resposta"

        # O score é atualizado a cada resposta (feedback imediato).
        score = self.scores.add_points(username, points)

        attempt = {
            "username": username,
            "session_id": session_id,
            "level": question["level"],
            "topic": question["topic"],
            "question_type": question.get("question_type", "fixa"),
            "question": question["question"],
            # Guardamos opções e índice correto para o modo treino reutilizar.
            "options": options,
            "correct_index": correct_index,
            "selected_answer": selected_answer,
            "correct_answer": options[correct_index],
            "is_correct": is_correct,
            "points": points,
            "response_time_seconds": round(max(0, time.time() - started_at), 2),
            "score_after_attempt": score,
            "timestamp": time.time(),
        }
        result = {"is_correct": is_correct, "points": points, "score": score,
                  "correct_answer": options[correct_index]}
        return attempt, result

    def save_session_attempts(self, attempts):
        """Guarda as tentativas de uma sessão usando uma Stack (LIFO).

        As tentativas são empilhadas e depois retiradas com pop(). Como a Stack
        inverte a ordem, voltamos a inverter para manter a ordem cronológica em
        attempts.json.
        """
        stack = Stack()
        for attempt in attempts:
            stack.push(attempt)
        retirados = []
        while not stack.is_empty():
            retirados.append(stack.pop())
        retirados.reverse()

        guardados = load("attempts.json", [])
        guardados.extend(retirados)
        save("attempts.json", guardados)

    def save_session_summary(self, username, session_id, level, attempts):
        """Guarda um resumo da sessão em sessions.json e devolve-o."""
        correct = sum(1 for attempt in attempts if attempt["is_correct"])
        points = sum(attempt["points"] for attempt in attempts)
        final_score = attempts[-1]["score_after_attempt"] if attempts else self.scores.get_score(username)
        summary = {
            "session_id": session_id,
            "username": username,
            "level": level,
            "datetime": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total": len(attempts),
            "correct": correct,
            "wrong": len(attempts) - correct,
            "session_points": points,
            "final_score": final_score,
        }
        sessions = load("sessions.json", [])
        sessions.append(summary)
        save("sessions.json", sessions)
        return summary

    # ------------------------------------------------------------------
    # Modo treino (perguntas erradas anteriores)
    # ------------------------------------------------------------------
    def wrong_questions_for(self, username):
        """Devolve as perguntas onde o utilizador falhou (para treino).

        Reconstrói cada pergunta a partir de attempts.json e coloca-as numa
        Queue (FIFO) para o aluno repetir.
        """
        queue = Queue()
        seen = set()
        for attempt in self.history_for(username):
            if attempt["is_correct"]:
                continue
            # Só conseguimos repetir tentativas que guardaram as opções.
            if "options" not in attempt or "correct_index" not in attempt:
                continue
            if attempt["question"] in seen:
                continue
            seen.add(attempt["question"])
            queue.enqueue({
                "level": attempt["level"],
                "topic": attempt["topic"],
                "question_type": attempt.get("question_type", "fixa"),
                "question": attempt["question"],
                "options": attempt["options"],
                "correct_index": attempt["correct_index"],
                "points_correct": 0,
                "points_wrong": 0,
            })
        questions = []
        while not queue.is_empty():
            questions.append(queue.dequeue())
        return questions

    def check_training_answer(self, question, selected_index):
        """Corrige uma resposta do modo treino sem alterar o score."""
        options = question["options"]
        valid_answer = 0 <= selected_index < len(options)
        correct_index = question["correct_index"]
        is_correct = valid_answer and selected_index == correct_index
        return {"is_correct": is_correct, "correct_answer": options[correct_index]}
