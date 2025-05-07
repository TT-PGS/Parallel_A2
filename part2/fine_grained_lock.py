import threading

class Node:
    def __init__(self, val):
        self.val = val
        self.next = None
        self.lock = threading.Lock()

class FineGrainedSet:
    def __init__(self):
        # hai sentinel: head đến -∞, tail đến +∞
        self.head = Node(float('-inf'))
        self.tail = Node(float('inf'))
        self.head.next = self.tail

    def _find(self, val):
        prev = self.head
        prev.lock.acquire()
        curr = prev.next
        curr.lock.acquire()
        while curr.val < val:
            prev.lock.release()
            prev, curr = curr, curr.next
            curr.lock.acquire()
        return prev, curr

    def add(self, val) -> bool:
        prev, curr = self._find(val)
        added = False
        if curr.val != val:
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
        if curr.val == val:
            prev.next = curr.next
            removed = True
        curr.lock.release()
        prev.lock.release()
        return removed

    def contains(self, val) -> bool:
        prev, curr = self._find(val)
        found = (curr.val == val)
        curr.lock.release()
        prev.lock.release()
        return found
