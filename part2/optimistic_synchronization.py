import threading

class Node:
    def __init__(self, val):
        self.val = val  # có thể là tuple như (x, y)
        self.next = None
        self.lock = threading.Lock()

class OptimisticSet:
    def __init__(self):
        # Dùng tuple để tránh lỗi so sánh với val là tọa độ
        inf = float('inf')
        self.head = Node(('HEAD',))
        self.tail = Node(('TAIL',))
        self.head.next = self.tail

    def _compare(self, a, b):
        if a == ('HEAD',): return -1
        if b == ('TAIL',): return -1
        if a == ('TAIL',): return 1
        if b == ('HEAD',): return 1

        # Convert scalars to tuple to unify comparison
        if not isinstance(a, tuple):
            a = (a,)
        if not isinstance(b, tuple):
            b = (b,)

        return (a > b) - (a < b)

    def _find(self, val):
        """
        Tìm vị trí prev và curr sao cho prev.val < val <= curr.val
        """
        prev, curr = self.head, self.head.next
        while self._compare(curr.val, val) < 0:
            prev, curr = curr, curr.next
        return prev, curr

    def _validate(self, prev, curr):
        """
        Đảm bảo prev vẫn trỏ tới curr sau khi acquire lock.
        """
        node = self.head
        while self._compare(node.val, prev.val) <= 0:
            if node is prev:
                return prev.next is curr
            node = node.next
        return False

    def add(self, val) -> bool:
        while True:
            prev, curr = self._find(val)
            prev.lock.acquire()
            curr.lock.acquire()
            try:
                if self._validate(prev, curr):
                    if self._compare(curr.val, val) != 0:
                        node = Node(val)
                        node.next = curr
                        prev.next = node
                        return True
                    else:
                        return False
            finally:
                curr.lock.release()
                prev.lock.release()

    def remove(self, val) -> bool:
        while True:
            prev, curr = self._find(val)
            prev.lock.acquire()
            curr.lock.acquire()
            try:
                if self._validate(prev, curr):
                    if self._compare(curr.val, val) == 0:
                        prev.next = curr.next
                        return True
                    else:
                        return False
            finally:
                curr.lock.release()
                prev.lock.release()

    def contains(self, val) -> bool:
        while True:
            prev, curr = self._find(val)
            prev.lock.acquire()
            curr.lock.acquire()
            try:
                if self._validate(prev, curr):
                    return self._compare(curr.val, val) == 0
            finally:
                curr.lock.release()
                prev.lock.release()
