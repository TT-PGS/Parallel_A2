import threading

class Node:
    def __init__(self, key):
        self.key = key
        self.next = None
        self.lock = threading.Lock()  # Per-node lock

class OptimisticSet:
    def __init__(self):
        self.head = Node(float('-inf'))
        self.tail = Node(float('inf'))
        self.head.next = self.tail

    def _validate(self, pred, curr):
        node = self.head
        while node.key <= pred.key:
            if node == pred:
                return pred.next == curr
            node = node.next
        return False

    def add(self, key):
        while True:
            pred = self.head
            curr = pred.next
            while curr.key < key:
                pred = curr
                curr = curr.next
            pred.lock.acquire()
            curr.lock.acquire()
            try:
                if self._validate(pred, curr):
                    if curr.key == key:
                        return False
                    new_node = Node(key)
                    new_node.next = curr
                    pred.next = new_node
                    return True
            finally:
                curr.lock.release()
                pred.lock.release()

    def remove(self, key):
        while True:
            pred = self.head
            curr = pred.next
            while curr.key < key:
                pred = curr
                curr = curr.next
            pred.lock.acquire()
            curr.lock.acquire()
            try:
                if self._validate(pred, curr):
                    if curr.key != key:
                        return False
                    pred.next = curr.next
                    return True
            finally:
                curr.lock.release()
                pred.lock.release()

    def contains(self, key):
        while True:
            pred = self.head
            curr = pred.next
            while curr.key < key:
                pred = curr
                curr = curr.next
            pred.lock.acquire()
            curr.lock.acquire()
            try:
                if self._validate(pred, curr):
                    return curr.key == key
            finally:
                curr.lock.release()
                pred.lock.release()
