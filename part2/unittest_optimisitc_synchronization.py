import unittest
import threading
from part2.optimistic_synchronization import OptimisticSet  # adjust import as needed

class TestOptimisticSet(unittest.TestCase):
    def setUp(self):
        self.set = OptimisticSet()

    # --- Single‐threaded “smoke” tests ---
    def test_add_and_contains(self):
        # initially empty
        self.assertFalse(self.set.contains(42))
        # first add should succeed
        self.assertTrue(self.set.add(42))
        self.assertTrue(self.set.contains(42))
        # duplicate add should fail
        self.assertFalse(self.set.add(42))

    def test_remove(self):
        self.set.add(7)
        self.assertTrue(self.set.contains(7))
        # remove existing element
        self.assertTrue(self.set.remove(7))
        self.assertFalse(self.set.contains(7))
        # remove non‐existent should fail
        self.assertFalse(self.set.remove(7))

    def test_mixed_sequence(self):
        # interleaved adds and removes
        self.assertTrue(self.set.add(1))
        self.assertTrue(self.set.add(2))
        self.assertTrue(self.set.remove(1))
        self.assertFalse(self.set.contains(1))
        self.assertTrue(self.set.contains(2))
        self.assertTrue(self.set.add(1))
        self.assertTrue(self.set.contains(1))

    # --- Multithreaded tests ---
    def test_concurrent_add_unique(self):
        N = 100
        threads = [threading.Thread(target=lambda i=i: self.set.add(i))
                   for i in range(N)]
        for t in threads: t.start()
        for t in threads: t.join()

        for i in range(N):
            self.assertTrue(self.set.contains(i),
                            f"Missing {i} after concurrent adds")

    def test_concurrent_add_same(self):
        N = 20
        results = []
        lock = threading.Lock()
        def worker():
            r = self.set.add(123)
            with lock:
                results.append(r)

        threads = [threading.Thread(target=worker) for _ in range(N)]
        for t in threads: t.start()
        for t in threads: t.join()

        # exactly one True, rest False
        self.assertEqual(results.count(True), 1)
        self.assertEqual(results.count(False), N-1)

    def test_concurrent_add_remove(self):
        # preload 0..99
        for i in range(100):
            self.set.add(i)

        def add_evens():
            for i in range(0, 100, 2):
                self.set.add(i)

        def remove_odds():
            for i in range(1, 100, 2):
                self.set.remove(i)

        t1 = threading.Thread(target=add_evens)
        t2 = threading.Thread(target=remove_odds)
        t1.start()
        t2.start()
        t1.join()
        t2.join()

        for i in range(100):
            if i % 2 == 0:
                self.assertTrue(self.set.contains(i), f"Even {i} missing")
            else:
                self.assertFalse(self.set.contains(i), f"Odd {i} still present")

if __name__ == '__main__':
    unittest.main()
