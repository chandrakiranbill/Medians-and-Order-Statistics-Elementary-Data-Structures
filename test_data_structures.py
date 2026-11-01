import unittest

from data_structures import (
    ArrayQueue, ArrayStack, DynamicArray, LinkedQueue, LinkedStack, Matrix,
    NaiveArrayQueue, RootedTree, SinglyLinkedList,
)


class TestDynamicArray(unittest.TestCase):
    def test_append_access_resize(self):
        a = DynamicArray()
        for i in range(100):
            a.append(i)
        self.assertEqual(len(a), 100)
        self.assertGreaterEqual(a.capacity, 100)
        self.assertEqual(a[0], 0)
        self.assertEqual(a[-1], 99)
        a[5] = "x"
        self.assertEqual(a[5], "x")

    def test_insert_delete(self):
        a = DynamicArray([1, 2, 4])
        a.insert(2, 3)
        a.insert(0, 0)
        a.insert(len(a), 5)
        self.assertEqual(a.to_list(), [0, 1, 2, 3, 4, 5])
        self.assertEqual(a.delete(0), 0)
        self.assertEqual(a.delete(-1), 5)
        a.remove(3)
        self.assertEqual(a.to_list(), [1, 2, 4])
        self.assertIn(4, a)
        self.assertEqual(a.index_of(99), -1)

    def test_shrink(self):
        a = DynamicArray(range(64))
        cap = a.capacity
        while len(a) > 2:
            a.pop()
        self.assertLess(a.capacity, cap)

    def test_errors(self):
        a = DynamicArray()
        with self.assertRaises(IndexError):
            a[0]
        with self.assertRaises(IndexError):
            a.pop()
        with self.assertRaises(IndexError):
            a.insert(5, 1)
        with self.assertRaises(ValueError):
            a.remove(1)


class TestMatrix(unittest.TestCase):
    def test_access_and_ops(self):
        m = Matrix.from_lists([[1, 2], [3, 4]])
        self.assertEqual(m[1, 0], 3)
        m[0, 1] = 9
        self.assertEqual(m.to_lists(), [[1, 9], [3, 4]])
        self.assertEqual(m.transpose().to_lists(), [[1, 3], [9, 4]])
        self.assertEqual((m + m).to_lists(), [[2, 18], [6, 8]])

    def test_matmul(self):
        a = Matrix.from_lists([[1, 2, 3], [4, 5, 6]])
        b = Matrix.from_lists([[7, 8], [9, 10], [11, 12]])
        self.assertEqual((a @ b).to_lists(), [[58, 64], [139, 154]])

    def test_row_col_insert_delete(self):
        m = Matrix.from_lists([[1, 2], [3, 4]])
        m.insert_row(1, [5, 6])
        self.assertEqual(m.to_lists(), [[1, 2], [5, 6], [3, 4]])
        m.insert_col(0, [0, 0, 0])
        self.assertEqual(m.to_lists(), [[0, 1, 2], [0, 5, 6], [0, 3, 4]])
        self.assertEqual(m.delete_col(1), [1, 5, 3])
        self.assertEqual(m.delete_row(0), [0, 2])
        self.assertEqual(m.to_lists(), [[0, 6], [0, 4]])

    def test_errors(self):
        m = Matrix(2, 2)
        with self.assertRaises(IndexError):
            m[2, 0]
        with self.assertRaises(ValueError):
            Matrix.from_lists([[1], [1, 2]])
        with self.assertRaises(ValueError):
            Matrix(2, 3) @ Matrix(2, 3)


class TestStacks(unittest.TestCase):
    def _run(self, s):
        self.assertTrue(s.is_empty())
        for i in range(50):
            s.push(i)
        self.assertEqual(len(s), 50)
        self.assertEqual(s.peek(), 49)
        self.assertEqual([s.pop() for _ in range(50)], list(range(49, -1, -1)))
        with self.assertRaises(IndexError):
            s.pop()
        with self.assertRaises(IndexError):
            s.peek()

    def test_array_stack(self):
        self._run(ArrayStack())

    def test_linked_stack(self):
        self._run(LinkedStack())


class TestQueues(unittest.TestCase):
    def _run(self, q):
        for i in range(10):
            q.enqueue(i)
        out = [q.dequeue() for _ in range(5)]
        for i in range(10, 30):  # forces wrap-around + resize in ring buffer
            q.enqueue(i)
        out += [q.dequeue() for _ in range(len(q))]
        self.assertEqual(out, list(range(30)))
        with self.assertRaises(IndexError):
            q.dequeue()

    def test_array_queue(self):
        q = ArrayQueue(capacity=4)
        self._run(q)
        q.enqueue("a")
        self.assertEqual(q.peek(), "a")

    def test_linked_queue(self):
        self._run(LinkedQueue())

    def test_naive_queue(self):
        self._run(NaiveArrayQueue())


class TestSinglyLinkedList(unittest.TestCase):
    def test_insertions(self):
        l = SinglyLinkedList()
        l.append(2)
        l.prepend(1)
        l.append(4)
        l.insert_at(2, 3)
        l.insert_at(0, 0)
        l.insert_at(len(l), 5)
        self.assertEqual(l.to_list(), [0, 1, 2, 3, 4, 5])
        node = l.find(5)
        l.insert_after(node, 6)
        self.assertEqual(l.tail.value, 6)

    def test_deletions(self):
        l = SinglyLinkedList(range(6))
        self.assertEqual(l.delete_head(), 0)
        self.assertEqual(l.delete_tail(), 5)
        self.assertTrue(l.delete(3))
        self.assertFalse(l.delete(99))
        self.assertEqual(l.delete_at(1), 2)
        self.assertEqual(l.to_list(), [1, 4])
        self.assertEqual(l.tail.value, 4)
        l.delete(4)
        self.assertEqual(l.tail.value, 1)
        l.delete_tail()
        self.assertTrue(l.is_empty())
        self.assertIsNone(l.head)
        self.assertIsNone(l.tail)
        with self.assertRaises(IndexError):
            l.delete_head()

    def test_traverse_search_reverse(self):
        l = SinglyLinkedList("abcd")
        seen = []
        l.traverse(seen.append)
        self.assertEqual(seen, list("abcd"))
        self.assertEqual(l.get(2), "c")
        self.assertEqual(l.index_of("d"), 3)
        self.assertIn("b", l)
        l.reverse()
        self.assertEqual(l.to_list(), list("dcba"))
        self.assertEqual(l.tail.value, "a")
        l.append("z")
        self.assertEqual(l.to_list(), list("dcbaz"))


class TestRootedTree(unittest.TestCase):
    def setUp(self):
        #        A
        #     /  |  \
        #    B   C   D
        #   / \      |
        #  E   F     G
        self.t = RootedTree("A")
        r = self.t.root
        d = self.t.add_child(r, "D")
        self.c = self.t.add_child(r, "C")
        b = self.t.add_child(r, "B")
        self.t.add_child(b, "F")
        self.e = self.t.add_child(b, "E")
        self.t.add_child(d, "G")

    def test_structure(self):
        self.assertEqual(len(self.t), 7)
        self.assertEqual([n.value for n in self.t.children(self.t.root)], ["B", "C", "D"])
        self.assertEqual(self.t.depth(self.e), 2)
        self.assertEqual(self.t.height(), 2)

    def test_traversals(self):
        self.assertEqual(list(self.t.preorder()), list("ABEFCDG"))
        self.assertEqual(list(self.t.level_order()), list("ABCDEFG"))
        self.assertIs(self.t.find("E"), self.e)
        self.assertIsNone(self.t.find("Z"))

    def test_remove(self):
        b = self.t.find("B")
        self.t.remove_subtree(b)
        self.assertEqual(len(self.t), 4)
        self.assertEqual(list(self.t.preorder()), list("ACDG"))
        self.t.remove_subtree(self.t.find("D"))
        self.assertEqual(list(self.t.preorder()), list("AC"))
        with self.assertRaises(ValueError):
            self.t.remove_subtree(self.t.root)


if __name__ == "__main__":
    unittest.main()
