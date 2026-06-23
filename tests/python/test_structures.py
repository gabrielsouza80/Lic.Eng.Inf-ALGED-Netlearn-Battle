"""Testes unitários simples para Queue e Stack."""
import unittest

from structures.queue import Queue
from structures.stack import Stack


class StructuresTests(unittest.TestCase):
    def test_queue_is_fifo(self):
        # FIFO: o primeiro valor colocado é o primeiro removido.
        queue = Queue()
        queue.enqueue("primeiro")
        queue.enqueue("segundo")
        self.assertEqual(queue.dequeue(), "primeiro")
        self.assertEqual(queue.dequeue(), "segundo")

    def test_stack_is_lifo(self):
        # LIFO: o último valor colocado é o primeiro removido.
        stack = Stack()
        stack.push("primeiro")
        stack.push("segundo")
        self.assertEqual(stack.pop(), "segundo")
        self.assertEqual(stack.pop(), "primeiro")


if __name__ == "__main__":
    unittest.main()
