import threading
import time
import argparse
import sys
import random
import os
from fine_grained_lock_ver2 import FineGrainedList as FineGrainedSet
from optimistic_synchronization_ver2 import OptimisticList as OptimisticSet
from collections import Counter

# Thiết lập đường dẫn log
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
RESULT_DIR = os.path.join(os.path.dirname(BASE_DIR), 'results', 'part2')
os.makedirs(RESULT_DIR, exist_ok=True)
LOG_FILE = os.path.join(RESULT_DIR, 'test_log.txt')

# Tham số test
N = 1000  # số cặp thao tác random
NUM_THREADS = 4
PERF_OPS = 10000

# Hàm ghi log vào file
def log(msg):
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(msg + '\n')

# Test correctness nâng cao
def test_correctness(cls, name, N):
    log(f"-- Testing correctness of {name}")
    s = cls()

    # 1) Kiểm tra idempotence cơ bản
    assert not s.contains(0), "contains(0) phải False khi mới tạo"
    assert s.add(0), "add(0) phải True lần đầu"
    assert not s.add(0), "add(0) phải False lần 2"
    assert s.contains(0), "contains(0) phải True sau add"
    assert s.remove(0), "remove(0) phải True khi tồn tại"
    assert not s.remove(0), "remove(0) lần 2 phải False"
    assert not s.contains(0), "contains(0) phải False sau remove"

    # 2) Tạo danh sách thao tác ngẫu nhiên
    ops = []
    random.seed(42)
    max_val = N // 2
    for _ in range(N):
        x = random.randint(0, max_val)
        ops.append(('add', x))
        ops.append(('remove', x))
    random.shuffle(ops)

    # 3) Counters để ghi nhận số lần thành công
    adds_success = Counter()
    removes_success = Counter()
    counter_lock = threading.Lock()

    # worker thực thi ops
    def worker(chunk):
        for op, x in chunk:
            if op == 'add':
                if s.add(x):
                    with counter_lock:
                        adds_success[x] += 1
            else:
                if s.remove(x):
                    with counter_lock:
                        removes_success[x] += 1

    # 4) Chia ops cho thread
    chunks = [ops[i::NUM_THREADS] for i in range(NUM_THREADS)]
    threads = [threading.Thread(target=worker, args=(chunks[i],)) for i in range(NUM_THREADS)]
    for t in threads: t.start()
    for t in threads: t.join()

    # 5) Tính expected set
    all_keys = set(adds_success) | set(removes_success)
    expected = {x for x in all_keys if adds_success[x] > removes_success[x]}

    # 6) Đọc actual từ s
    actual = {x for x in range(max_val+1) if s.contains(x)}

    # 7) So sánh
    assert actual == expected, (
        f"{name} final state mismatch:\n"
        f"  Expected ({len(expected)}): {sorted(expected)}\n"
        f"  Actual   ({len(actual)}): {sorted(actual)}"
    )

    log(f"✅ {name}: PASS correctness")

# Test performance
def test_performance(cls, name):
    log(f"-- Testing performance of {name}")
    s = cls()

    def add_remove_mix():
        for i in range(PERF_OPS):
            s.add(i)
            if i % 2 == 0:
                s.remove(i)

    threads = [threading.Thread(target=add_remove_mix) for _ in range(NUM_THREADS)]
    start = time.perf_counter()
    for t in threads: t.start()
    for t in threads: t.join()
    duration = time.perf_counter() - start
    log(f"⏱ {name} completed in {duration:.4f} seconds")

if __name__ == '__main__':
    # Khởi tạo file log
    with open(LOG_FILE, 'w', encoding='utf-8') as f:
        f.write("=== Test Log ===\n")

    # Chạy correctness tests
    for cls, name in [(FineGrainedSet, 'FineGrainedSet'), (OptimisticSet, 'OptimisticSet')]:
        try:
            test_correctness(cls, name, N)
        except AssertionError as e:
            log(f"❌ {name}: FAIL correctness")
            log(f"Reason: {e}")

    # Chạy performance tests
    for cls, name in [(FineGrainedSet, 'FineGrainedSet'), (OptimisticSet, 'OptimisticSet')]:
        try:
            test_performance(cls, name)
        except Exception as e:
            log(f"❌ {name}: ERROR performance")
            log(f"Reason: {e}")
