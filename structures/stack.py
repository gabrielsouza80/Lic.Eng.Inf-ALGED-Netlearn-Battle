"""[Secção 25] Pilha Stack usada para guardar tentativas."""


class Stack:
    """[Secção 25] LIFO: a última tentativa a entrar é a primeira a sair."""
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
