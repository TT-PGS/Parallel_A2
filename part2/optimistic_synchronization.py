import threading

class Node:
    def __init__(self, val):
        self.val = val
        self.next = None
        self.lock = threading.Lock()

class OptimisticSet:
    def __init__(self):
        self.head = Node(float('-inf'))
        self.tail = Node(float('inf'))
        self.head.next = self.tail

    def _find(self, val):
        prev, curr = self.head, self.head.next
        while str(curr.val) < str(val):
            prev, curr = curr, curr.next
        return prev, curr

    def _validate(self, prev, curr):
        node = self.head
        # đơn giản duyệt lại xem prev→next có phải curr không
        while str(node.val) <= str(prev.val):
            if node is prev:
                return prev.next is curr
            node = node.next
        return False

    def add(self, val) -> bool:
        while True:
            prev, curr = self._find(val)
            prev.lock.acquire()
            curr.lock.acquire()
            if self._validate(prev, curr):
                if curr.val != val:
                    node = Node(val)
                    node.next = curr
                    prev.next = node
                    added = True
                else:
                    added = False
                curr.lock.release()
                prev.lock.release()
                return added
            curr.lock.release()
            prev.lock.release()

    def remove(self, val) -> bool:
        while True:
            prev, curr = self._find(val)
            prev.lock.acquire()
            curr.lock.acquire()
            if self._validate(prev, curr):
                if curr.val == val:
                    prev.next = curr.next
                    removed = True
                else:
                    removed = False
                curr.lock.release()
                prev.lock.release()
                return removed
            curr.lock.release()
            prev.lock.release()

    def contains(self, val) -> bool:
        while True:
            prev, curr = self._find(val)
            prev.lock.acquire()
            curr.lock.acquire()

            if self._validate(prev, curr):
                contains = (curr.val == val)
                curr.lock.release()
                prev.lock.release()
                return contains

            curr.lock.release()
            prev.lock.release()
