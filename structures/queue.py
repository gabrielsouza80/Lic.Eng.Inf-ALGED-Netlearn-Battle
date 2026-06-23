"""[Secção 24] Fila Queue usada para organizar perguntas."""


class Queue:
    """[Secção 24] FIFO: a primeira pergunta a entrar é a primeira a sair."""
    def __init__(self):
        self._items = []

    def enqueue(self, item):
        self._items.append(item)

    def dequeue(self):
        return None if self.is_empty() else self._items.pop(0)

    def is_empty(self):
        return len(self._items) == 0
