import threading

class Node:
    def __init__(self, key):
        self.key = key
        self.next = None
        self.lock = threading.Lock()  # Per-node lock

class FineGrainedSet:
    def __init__(self):
        self.head = Node(float('-inf'))
        self.tail = Node(float('inf'))
        self.head.next = self.tail

    def _lock_pair(self, pred, curr):
        pred.lock.acquire()
        curr.lock.acquire()

    def _unlock_pair(self, pred, curr):
        curr.lock.release()
        pred.lock.release()

    def add(self, key):
        pred = self.head
        curr = pred.next
        while curr.key < key:
            pred = curr
            curr = curr.next
        self._lock_pair(pred, curr)
        try:
            if curr.key == key:
                return False
            new_node = Node(key)
            new_node.next = curr
            pred.next = new_node
            return True
        finally:
            self._unlock_pair(pred, curr)

    def remove(self, key):
        pred = self.head
        curr = pred.next
        while curr.key < key:
            pred = curr
            curr = curr.next
        self._lock_pair(pred, curr)
        try:
            if curr.key != key:
                return False
            pred.next = curr.next
            return True
        finally:
            self._unlock_pair(pred, curr)

    def contains(self, key):
        curr = self.head
        while curr.key < key:
            curr = curr.next
        return curr.key == key
