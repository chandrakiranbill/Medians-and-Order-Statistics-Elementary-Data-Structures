import random
import unittest

from selection import median_of_medians_select, randomized_select
from selection.deterministic import median as det_median
from selection.randomized import median as rand_median

ALGOS = [
    ("deterministic", lambda a, k: median_of_medians_select(a, k)),
    ("randomized", lambda a, k: randomized_select(a, k, seed=123)),
]


class TestSelection(unittest.TestCase):
    def check_all_ranks(self, arr):
        expected = sorted(arr)
        for name, f in ALGOS:
            for k in range(1, len(arr) + 1):
                with self.subTest(algo=name, k=k, n=len(arr)):
                    self.assertEqual(f(arr, k), expected[k - 1])

    def test_single_element(self):
        self.check_all_ranks([42])

    def test_small_arrays(self):
        self.check_all_ranks([3, 1, 2])
        self.check_all_ranks([5, 4, 3, 2, 1, 0])
        self.check_all_ranks(list(range(11)))

    def test_duplicates(self):
        self.check_all_ranks([5, 1, 5, 5, 2, 5, 1, 1, 9, 5, 5])
        self.check_all_ranks([7] * 50)
        self.check_all_ranks([0, 1] * 40)

    def test_sorted_and_reverse(self):
        self.check_all_ranks(list(range(200)))
        self.check_all_ranks(list(range(200, 0, -1)))

    def test_negative_and_floats(self):
        self.check_all_ranks([-3.5, 2.25, 0.0, -10, 7, 7, -3.5])

    def test_strings(self):
        self.check_all_ranks(list("thequickbrownfoxjumps"))

    def test_random_fuzz(self):
        rng = random.Random(0)
        for _ in range(200):
            n = rng.randint(1, 300)
            arr = [rng.randint(-50, 50) for _ in range(n)]
            k = rng.randint(1, n)
            expected = sorted(arr)[k - 1]
            for name, f in ALGOS:
                self.assertEqual(f(arr, k), expected, name)

    def test_input_not_modified(self):
        arr = [9, 3, 7, 1, 8, 2]
        copy = list(arr)
        median_of_medians_select(arr, 3)
        randomized_select(arr, 3)
        self.assertEqual(arr, copy)

    def test_in_place_option(self):
        arr = [9, 3, 7, 1, 8, 2]
        self.assertEqual(randomized_select(arr, 2, in_place=True), 2)
        self.assertEqual(sorted(arr), [1, 2, 3, 7, 8, 9])

    def test_invalid_inputs(self):
        for name, f in ALGOS:
            with self.subTest(algo=name):
                with self.assertRaises(ValueError):
                    f([], 1)
                with self.assertRaises(ValueError):
                    f([1, 2], 0)
                with self.assertRaises(ValueError):
                    f([1, 2], 3)
                with self.assertRaises(TypeError):
                    f([1, 2], 1.5)

    def test_medians(self):
        arr = [4, 1, 3, 2]
        self.assertEqual(det_median(arr), 2)
        self.assertEqual(rand_median(arr, seed=1), 2)
        self.assertEqual(det_median([5, 1, 3]), 3)

    def test_large(self):
        rng = random.Random(1)
        arr = [rng.random() for _ in range(20001)]
        s = sorted(arr)
        for k in (1, 10000, 20001):
            self.assertEqual(median_of_medians_select(arr, k), s[k - 1])
            self.assertEqual(randomized_select(arr, k, seed=k), s[k - 1])


if __name__ == "__main__":
    unittest.main()
