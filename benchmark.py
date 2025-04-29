import threading
from concurrent.futures import ThreadPoolExecutor
import math
from common import euclidean_heuristic, speeds, log_common

class _PLLNode:
    __slots__ = ('node', 'f', 'g', 't', 'prev', 'next')
    def __init__(self, node, f, g, t):
        self.node = node
        self.f = f
        self.g = g
        self.t = t
        self.prev = self.next = None

class PriorityLinkedList:
    def __init__(self):
        self.head = _PLLNode(None, float('-inf'), 0, 0)
        self.tail = _PLLNode(None, float('inf'), 0, 0)
        self.head.next = self.tail
        self.tail.prev = self.head
        self._map = {}
        self._lock = threading.Lock()

    def push_or_update(self, node_id, f, g, t):
        with self._lock:
            if node_id in self._map:
                elem = self._map[node_id]
                if f >= elem.f:
                    return
                elem.prev.next = elem.next
                elem.next.prev = elem.prev
            else:
                elem = _PLLNode(node_id, f, g, t)
                self._map[node_id] = elem
            curr = self.tail.prev
            while curr is not self.head and curr.f > f:
                curr = curr.prev
            elem.next = curr.next
            elem.prev = curr
            curr.next.prev = elem
            curr.next = elem

    def pop_min(self):
        with self._lock:
            first = self.head.next
            if first is self.tail:
                raise IndexError("pop from empty PriorityLinkedList")
            self.head.next = first.next
            first.next.prev = self.head
            node = first.node
            del self._map[node]
            return node, first.f, first.g, first.t

    def is_empty(self):
        with self._lock:
            return self.head.next is self.tail

class AStarWorker:
    def __init__(self, graph, destination, heuristic, speeds,
                 g_scores, preds, open_set, g_lock, pred_lock):
        self.graph = graph
        self.destination = destination
        self.heuristic = heuristic
        self.speeds = speeds or []
        self.g_scores = g_scores
        self.preds = preds
        self.open_set = open_set
        self.g_lock = g_lock
        self.pred_lock = pred_lock

    def relax_job(self, job):
        u, nbr, length, g_u, t_u = job
        speed = (self.speeds[math.floor(t_u)]
                 if self.speeds and math.floor(t_u) < len(self.speeds)
                 else 1.0)
        travel = length / speed
        g_n = g_u + travel
        t_n = t_u + travel
        h_n = self.heuristic(self.graph, nbr, self.destination, t_n)
        f_n = g_n + h_n
        with self.g_lock:
            if g_n < self.g_scores.get(nbr, float('inf')):
                self.g_scores[nbr] = g_n
                with self.pred_lock:
                    self.preds[nbr] = u
                self.open_set.push_or_update(nbr, f_n, g_n, t_n)


def parallel_astar_linkedlist(graph, origin, destination,
                              heuristic=euclidean_heuristic,
                              speeds=speeds,
                              max_workers=4):
    # log_common(f"[Parallel A*] Starting with {max_workers} workers.")
    if origin not in graph or destination not in graph:
        # log_common("Origin or destination not in graph (parallel).")
        return None, None
    if origin == destination:
        return [origin], 0.0

    g_scores = {origin: 0.0}
    preds = {}
    closed = set()
    open_set = PriorityLinkedList()
    h0 = heuristic(graph, origin, destination, 0.0)
    open_set.push_or_update(origin, h0, 0.0, 0.0)

    while True:
        try:
            current, f_cur, g_cur, t_cur = open_set.pop_min()
        except IndexError:
            # log_common("Open set empty, no path (parallel).")
            return None, None

        if f_cur > g_scores.get(current, float('inf')) + \
               heuristic(graph, current, destination, t_cur):
            continue

        if current == destination:
            # log_common("Destination reached (parallel).")
            path = []
            node = destination
            while node != origin:
                path.append(node)
                node = preds[node]
            path.append(origin)
            return path[::-1], g_scores[destination]

        closed.add(current)
        jobs = []
        for nbr, data in graph[current].items():
            if nbr in closed:
                continue
            length = data.get('length', 1.0)
            jobs.append((current, nbr, length, g_cur, t_cur))

        g_lock = threading.Lock()
        pred_lock = threading.Lock()
        with ThreadPoolExecutor(max_workers=max_workers) as pool:
            pool.map(AStarWorker(
                graph, destination, heuristic, speeds,
                g_scores, preds, open_set,
                g_lock, pred_lock
            ).relax_job, jobs)