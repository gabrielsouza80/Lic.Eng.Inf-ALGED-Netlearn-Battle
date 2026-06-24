"""Pilha Stack (LIFO) usada como armazenamento temporário antes da persistência.

Durante uma sessão, cada tentativa é colocada na Stack com push().
No final da validação, a tentativa é retirada com pop() e guardada em
attempts.json. O uso de Stack é uma demonstração académica do conceito LIFO:
a última tentativa a entrar é a primeira a sair.
"""


class Stack:
    """LIFO: a última tentativa a entrar (push) é a primeira a sair (pop)."""
    def __init__(self):
        self._items = []

    def push(self, item):
        self._items.append(item)

    def pop(self):
        return None if self.is_empty() else self._items.pop()

    def peek(self):
        return None if self.is_empty() else self._items[-1]

    def is_empty(self):
        return len(self._items) == 0
