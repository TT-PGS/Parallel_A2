import threading
import unittest
import time
import os
import random
from collections import Counter

from part2.fine_grained_lock import FineGrainedSet
from part2.optimistic_synchronization import OptimisticSet

# Directory for logs and results
RESULT_DIR = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), 'results', 'part2'
)
os.makedirs(RESULT_DIR, exist_ok=True)
LOG_FILE = os.path.join(RESULT_DIR, 'test_log.txt')

def log(msg):
    """
    Append a message to the test log file.
    """
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(msg + '\n')

def run_correctness_test(test_case, SET_CLASS, SET_NAME, OPS, THREADS):
    """
    Perform correctness testing for a concurrent set implementation.

    This test checks that under concurrent operations, the set maintains 
    correct add/remove/contains semantics. It runs randomized operations
    and compares the actual final set content with the expected one.

    Args:
        test_case (unittest.TestCase): the active test case instance
        SET_CLASS (class): the set class under test
        SET_NAME (str): the name for logging purposes
        OPS (int): number of operations
        THREADS (int): number of concurrent threads
    """
    log(f"-- Testing correctness of {SET_NAME}")
    s = SET_CLASS()

    test_case.assertFalse(s.contains(0), 'contains(0) on new set must be False')
    test_case.assertTrue(s.add(0), 'add(0) first time must return True')
    test_case.assertFalse(s.add(0), 'add(0) second time must return False')
    test_case.assertTrue(s.contains(0), 'contains(0) after add must be True')
    test_case.assertTrue(s.remove(0), 'remove(0) when present must return True')
    test_case.assertFalse(s.remove(0), 'remove(0) second time must return False')
    test_case.assertFalse(s.contains(0), 'contains(0) after remove must be False')

    ops = []
    random.seed(42)
    max_val = OPS // 2
    for _ in range(OPS):
        x = random.randint(0, max_val)
        ops.extend([('add', x), ('remove', x)])
    random.shuffle(ops)

    adds_success = Counter()
    removes_success = Counter()
    counter_lock = threading.Lock()

    def worker(chunk_ops):
        for op, x in chunk_ops:
            result = s.add(x) if op == 'add' else s.remove(x)
            if result:
                with counter_lock:
                    (adds_success if op == 'add' else removes_success)[x] += 1

    chunks = [ops[i::THREADS] for i in range(THREADS)]
    threads = [threading.Thread(target=worker, args=(chunks[i],)) for i in range(THREADS)]
    for t in threads: t.start()
    for t in threads: t.join()

    expected = {
        x for x in set(adds_success) | set(removes_success)
        if adds_success[x] > removes_success[x]
    }
    actual = {x for x in range(max_val + 1) if s.contains(x)}

    test_case.assertEqual(
        actual,
        expected,
        f"{SET_NAME} final state mismatch\n"
        f"Expected ({len(expected)} items): {sorted(expected)}\n"
        f"Actual   ({len(actual)} items): {sorted(actual)}"
    )
    log(f"✅ {SET_NAME}: PASS correctness")

def run_performance_test(SET_CLASS, SET_NAME, OPS, THREAD_COUNTS):
    """
    Perform performance benchmarking for a concurrent set implementation.

    This test measures the execution time of a mix of add/remove operations
    across multiple thread counts.

    Args:
        SET_CLASS (class): the set class under test
        SET_NAME (str): label for log output
        OPS (int): number of operations per thread
        THREAD_COUNTS (list[int]): thread counts to test
    """
    for num_threads in THREAD_COUNTS:
        log(f"-- Testing performance of {SET_NAME} with {num_threads} threads")
        s = SET_CLASS()

        def mix_ops():
            for i in range(OPS):
                s.add(i)
                if i % 2 == 0:
                    s.remove(i)

        threads = [threading.Thread(target=mix_ops) for _ in range(num_threads)]
        start = time.perf_counter()
        for t in threads: t.start()
        for t in threads: t.join()
        duration = time.perf_counter() - start
        log(f"⏱ {SET_NAME} with {num_threads} threads completed in {duration:.4f} seconds")

class TestFineGrainedSet(unittest.TestCase):
    def setUp(self):
        self.THREAD = 4
        self.THREADS = [1, 2, 4, 8, 12]
        self.OPS = 1000

    def test_01_finegrained_correctness(self):
        """Test correctness of FineGrainedSet under concurrent operations."""
        run_correctness_test(self, FineGrainedSet, 'FineGrainedSet', self.OPS, self.THREAD)

    def test_02_finegrained_performance(self):
        """Benchmark FineGrainedSet with increasing thread counts."""
        run_performance_test(FineGrainedSet, 'FineGrainedSet', self.OPS, self.THREADS)

class TestOptimisticSet(unittest.TestCase):
    def setUp(self):
        self.THREAD = 4
        self.THREADS = [1, 2, 4, 8, 12]
        self.OPS = 1000

    def test_01_optimistic_correctness(self):
        """Test correctness of OptimisticSet under concurrent operations."""
        run_correctness_test(self, OptimisticSet, 'OptimisticSet', self.OPS, self.THREAD)

    def test_02_optimistic_performance(self):
        """Benchmark OptimisticSet with increasing thread counts."""
        run_performance_test(OptimisticSet, 'OptimisticSet', self.OPS, self.THREADS)

if __name__ == '__main__':
    with open(LOG_FILE, 'w', encoding='utf-8') as f:
        f.write("=== Test Log ===\n")
    unittest.main()
