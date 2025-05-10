import threading
import math
import time
from queue import PriorityQueue, Empty
from collections import defaultdict
from part2.fine_grained_lock import FineGrainedSet
from part2.optimistic_synchronization import OptimisticSet

def get_edge_cost(graph, u, v):
    """
    Extract the edge cost from graph between nodes u and v.
    Default to 1.0 if not found.
    """
    try:
        edge = graph[u][v][0]
        if isinstance(edge, tuple):
            edge = edge[2]
        return edge.get('length', 1.0)
    except Exception:
        return 1.0

def euclidean_h(u, v, graph):
    """
    Heuristic function: Euclidean distance between u and v.
    If coordinates are missing, return 0.
    """
    try:
        x1, y1 = graph.nodes[u]['x'], graph.nodes[u]['y']
        x2, y2 = graph.nodes[v]['x'], graph.nodes[v]['y']
        return math.hypot(x2 - x1, y2 - y1)
    except KeyError:
        return 0.0

def is_within_ellipse(p, a, b, graph, factor=100):
    """
    Determines if point p lies within an ellipse with foci a and b.
    This is used for pruning far nodes in A*.
    """
    try:
        xa, ya = graph.nodes[a]['x'], graph.nodes[a]['y']
        xb, yb = graph.nodes[b]['x'], graph.nodes[b]['y']
        xp, yp = graph.nodes[p]['x'], graph.nodes[p]['y']
        total = math.hypot(xa - xp, ya - yp) + math.hypot(xb - xp, yb - yp)
        max_range = factor * math.hypot(xa - xb, ya - yb)
        return total <= max_range
    except KeyError:
        return True

def astar_parallel(start, goal, graph, h_func, f_vector_func=None, version="FineGrain", num_threads=4):
    print(f"[Main] Starting A* from {start} to {goal} with {num_threads} threads using {version}")

    open_queues = [PriorityQueue() for _ in range(num_threads)]
    visited = FineGrainedSet() if version == "FineGrain" else OptimisticSet()
    g_score = defaultdict(lambda: float('inf'))
    g_score[start] = 0.0

    g_lock = threading.Lock()
    best_goal_lock = threading.Lock()
    stop_event = threading.Event()

    result = {
        'path': None,
        'f_vec': [float('inf'), float('inf')]
    }

    thread_done = [False] * num_threads
    empty_counter = [0] * num_threads
    done_lock = threading.Lock()

    h0 = h_func(start, goal, graph)
    open_queues[0].put(((h0, 0), start, 0.0, [start]))
    # print(f"[Main] Initial node {start} pushed with h={h0}")

    def worker(tid):
        # print(f"[Thread {tid}] Started")
        while not stop_event.is_set():
            found_work = False
            for i in range(num_threads):
                q = open_queues[(tid + i) % num_threads]
                try:
                    (f_val, hopper), node, g_val, path = q.get_nowait()
                    # print(f"[Thread {tid}] Got node {node} with f={f_val}, g={g_val}")
                    found_work = True
                    break
                except Empty:
                    continue

            if not found_work:
                empty_counter[tid] += 1
                if empty_counter[tid] > 200:
                    # print(f"[Thread {tid}] No work for too long. Exiting.")
                    with done_lock:
                        thread_done[tid] = True
                        if all(thread_done):
                            # print("[All Threads] Finished. Triggering stop event.")
                            stop_event.set()
                    return
                time.sleep(0.001)
                continue
            else:
                empty_counter[tid] = 0

            with best_goal_lock:
                if result['path'] is not None and f_val > result['f_vec'][0]:
                    # print(f"[Thread {tid}] Skipping node {node}, f_val {f_val} worse than best {result['f_vec'][0]}")
                    continue

            if visited.contains(node):
                # print(f"[Thread {tid}] Node {node} already visited")
                continue

            visited.add(node)
            # print(f"[Thread {tid}] Visiting node {node}")

            if node == goal:
                with best_goal_lock:
                    if f_val < result['f_vec'][0]:
                        result['path'] = path
                        result['f_vec'] = [f_val, hopper]
                        # print(f"[Thread {tid}] Goal {goal} reached! Path length: {len(path)}")
                        stop_event.set()
                        return

            for nbr in graph.neighbors(node):
                # print(f"[Thread {tid}] Checking neighbor {nbr} of {node}")
                edge_cost = get_edge_cost(graph, node, nbr)
                tentative_g = g_val + edge_cost
                new_hop = hopper + 1

                with g_lock:
                    existing = g_score[nbr]
                    if tentative_g > existing:
                        # print(f"[Thread {tid}] Skipping neighbor {nbr}, worse g={tentative_g} > {existing}")
                        continue
                    if tentative_g == existing and new_hop >= result['f_vec'][1]:
                        # print(f"[Thread {tid}] Skipping neighbor {nbr}, same g but hop {new_hop} worse or equal to best {result['f_vec'][1]}")
                        continue
                    g_score[nbr] = tentative_g
                    # print(f"[Thread {tid}] Updating g_score[{nbr}] = {tentative_g}")

                h_nbr = h_func(nbr, goal, graph)
                new_f = tentative_g + h_nbr
                open_queues[tid % num_threads].put(((new_f, new_hop), nbr, tentative_g, path + [nbr]))
                # print(f"[Thread {tid}] Pushed {nbr} with f={new_f}, g={tentative_g}, hop={new_hop}")

    threads = [threading.Thread(target=worker, args=(i,), daemon=True) for i in range(num_threads)]
    for t in threads: t.start()
    for t in threads: t.join()

    if result['path']:
        # print("[Main] A* completed. Returning result.")
        if f_vector_func:
            g = g_score[goal]
            h = h_func(goal, goal, graph)
            fvec = f_vector_func(g, h)
            if isinstance(fvec, tuple):
                fvec = list(fvec)
            elif isinstance(fvec, (float, int)):
                fvec = [fvec]
            return result['path'], fvec
        return result['path'], result['f_vec']
    else:
        # print("[Main] No path found.")
        return None, None
