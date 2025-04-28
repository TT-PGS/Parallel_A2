import math
import multiprocessing
from multiprocessing import Manager, Queue
from common import euclidean_heuristic, speeds, log_common

def worker(graph, destination, heuristic, speeds, in_queue, out_queue):
    while True:
        item = in_queue.get()
        if item is None:
            break
        current, g_cur, t_cur = item
        results = []
        for nbr, data in graph[current].items():
            length = data.get('length', 1.0)
            speed = speeds[math.floor(t_cur) % len(speeds)]
            travel = length / speed
            g_n = g_cur + travel
            t_n = t_cur + travel
            h_n = heuristic(graph, nbr, destination, t_n)
            f_n = g_n + h_n
            results.append((f_n, g_n, t_n, current, nbr))
        out_queue.put(results)

def multiprocessing_astar(graph, origin, destination,
                           heuristic=euclidean_heuristic,
                           speeds=speeds, num_workers=4):
    log_common(f"[Multiprocessing A*] Starting with {num_workers} workers.")
    if origin not in graph or destination not in graph:
        log_common("Origin or destination not in graph (multiprocessing).")
        return None, None
    if origin == destination:
        return [origin], 0.0

    manager = Manager()
    g_scores = manager.dict()
    preds = manager.dict()
    g_scores[origin] = 0.0

    open_set = [(heuristic(graph, origin, destination, 0.0), 0.0, 0.0, origin)]

    in_queue = Queue()
    out_queue = Queue()
    pool = []
    for _ in range(num_workers):
        p = multiprocessing.Process(target=worker,
                                     args=(graph, destination, heuristic, speeds, in_queue, out_queue))
        p.start()
        pool.append(p)

    closed = set()

    while open_set:
        open_set.sort()
        f_cur, g_cur, t_cur, current = open_set.pop(0)

        if current == destination:
            path = []
            node = destination
            while node != origin:
                path.append(node)
                node = preds[node]
            path.append(origin)
            for _ in pool:
                in_queue.put(None)
            for p in pool:
                p.join()
            return path[::-1], g_scores[destination]

        if current in closed:
            continue
        closed.add(current)

        in_queue.put((current, g_cur, t_cur))

        relaxations = out_queue.get()
        for f_n, g_n, t_n, u, nbr in relaxations:
            if g_n < g_scores.get(nbr, float('inf')):
                g_scores[nbr] = g_n
                preds[nbr] = u
                open_set.append((f_n, g_n, t_n, nbr))

    for _ in pool:
        in_queue.put(None)
    for p in pool:
        p.join()

    return None, None
