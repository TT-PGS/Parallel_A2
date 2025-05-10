import threading

class Node:
    def __init__(self, val):
        self.val = val  # giá trị (giả sử là tuple như (x, y))
        self.next = None
        self.lock = threading.Lock()

class FineGrainedSet:
    def __init__(self):
        # Sentinel nodes for -∞ and +∞
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
        prev = self.head
        prev.lock.acquire()
        curr = prev.next
        curr.lock.acquire()
        while self._compare(curr.val, val) < 0:
            prev.lock.release()
            prev, curr = curr, curr.next
            curr.lock.acquire()
        return prev, curr

    def add(self, val) -> bool:
        prev, curr = self._find(val)
        added = False
        if self._compare(curr.val, val) != 0:
            node = Node(val)
            node.next = curr
            prev.next = node
            added = True
        curr.lock.release()
        prev.lock.release()
        return added

    def remove(self, val) -> bool:
        prev, curr = self._find(val)
        removed = False
        if self._compare(curr.val, val) == 0:
            prev.next = curr.next
            removed = True
        curr.lock.release()
        prev.lock.release()
        return removed

    def contains(self, val) -> bool:
        prev, curr = self._find(val)
        found = self._compare(curr.val, val) == 0
        curr.lock.release()
        prev.lock.release()
        return found
