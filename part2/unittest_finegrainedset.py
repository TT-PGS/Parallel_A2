import unittest
import threading
from part2.fine_grained_lock import FineGrainedSet  # adjust to your module path

class TestFineGrainedSet(unittest.TestCase):
    """Unit tests for FineGrainedSet (a concurrent linked list set using fine-grained locking)."""

    def setUp(self):
        """Initialize a new FineGrainedSet before each test."""
        self.set = FineGrainedSet()

    # --- Single-threaded tests ---
    def test_add_and_contains(self):
        """Test that adding a value and checking its existence behaves correctly."""
        self.assertFalse(self.set.contains(10))
        self.assertTrue(self.set.add(10))
        self.assertTrue(self.set.contains(10))
        # duplicate add should return False
        self.assertFalse(self.set.add(10))

    def test_remove(self):
        """Test that removing values behaves correctly, including removing nonexistent ones."""
        self.set.add(5)
        self.assertTrue(self.set.contains(5))
        self.assertTrue(self.set.remove(5))
        self.assertFalse(self.set.contains(5))
        # removing again should return False
        self.assertFalse(self.set.remove(5))

    def test_add_remove_sequence(self):
        """Add a sequence of values, verify their presence, then remove and verify absence."""
        vals = [1, 2, 3, 4, 5]
        for v in vals:
            self.assertTrue(self.set.add(v))
        for v in vals:
            self.assertTrue(self.set.contains(v))
        for v in vals:
            self.assertTrue(self.set.remove(v))
        for v in vals:
            self.assertFalse(self.set.contains(v))

    # --- Multi-threaded tests ---
    def test_concurrent_add_unique(self):
        """
        Spawn N threads each adding a unique value.
        At the end, all values should be present in the set.
        """
        N = 50
        threads = []
        for i in range(N):
            t = threading.Thread(target=lambda x=i: self.set.add(x))
            threads.append(t)
            t.start()
        for t in threads:
            t.join()

        for i in range(N):
            self.assertTrue(self.set.contains(i), f"Value {i} missing after concurrent add")

    def test_concurrent_add_same_value(self):
        """
        Spawn N threads all trying to add the same value.
        Only one thread should succeed; others should fail due to duplication.
        """
        N = 20
        results = []
        lock = threading.Lock()

        def worker():
            r = self.set.add(99)
            with lock:
                results.append(r)

        threads = [threading.Thread(target=worker) for _ in range(N)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        self.assertEqual(results.count(True), 1, "Exactly one thread should succeed in adding")
        self.assertEqual(results.count(False), N - 1, "All other threads should see duplicate")

    def test_concurrent_add_remove_mixed(self):
        """
        Test mixed workload: spawn threads that add even numbers and remove odd numbers.
        Starting from a set preloaded with 0–99.
        Expected: all even numbers remain, all odd numbers removed.
        """
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
