import threading
import math
import heapq
import random
import time
from queue import PriorityQueue, Empty
from collections import defaultdict
from part2.fine_grained_lock import FineGrainedSet
from part2.optimistic_synchronization import OptimisticSet

def get_edge_cost(graph, u, v):
    try:
        edge = graph[u][v][0]
        if isinstance(edge, tuple):
            edge = edge[2]
        return edge.get('length', 1.0)
    except Exception:
        return 1.0

def euclidean_h(u, v, graph):
    try:
        x1, y1 = graph.nodes[u]['x'], graph.nodes[u]['y']
        x2, y2 = graph.nodes[v]['x'], graph.nodes[v]['y']
        return math.hypot(x2 - x1, y2 - y1)
    except:
        return 0.0

def is_within_ellipse(p, a, b, graph, factor=100):
    try:
        xa, ya = graph.nodes[a]['x'], graph.nodes[a]['y']
        xb, yb = graph.nodes[b]['x'], graph.nodes[b]['y']
        xp, yp = graph.nodes[p]['x'], graph.nodes[p]['y']
        total = math.hypot(xa - xp, ya - yp) + math.hypot(xb - xp, yb - yp)
        max_range = factor * math.hypot(xa - xb, ya - yb)
        return total <= max_range
    except:
        return True

def astar_parallel(start, goal, graph, h_func, f_vector_func=None, version="FineGrain", num_threads=4):
    open_queues = [PriorityQueue() for _ in range(num_threads)]
    visited = FineGrainedSet() if version == "FineGrain" else OptimisticSet()
    g_score = defaultdict(lambda: float('inf'))
    g_score[start] = 0.0
    g_lock = threading.Lock()
    best_goal_lock = threading.Lock()
    result = {'path': None, 'f_vec': [float('inf'), float('inf')]}

    h0 = h_func(start, goal, graph)
    open_queues[random.randint(0, num_threads - 1)].put(((h0, 0), start, 0.0, [start]))

    stop_event = threading.Event()
    thread_done = [False] * num_threads
    done_lock = threading.Lock()
    empty_counter = [0] * num_threads

    def worker(tid):
        print(f"Thread {tid} started")
        print(f"Thread {tid} is waiting for work")
        print(f"Thread {tid} is working")
        print(f"Thread {tid} is done")
        while not stop_event.is_set():
            success = False
            for i in range(num_threads):
                q = open_queues[(tid + i) % num_threads]
                try:
                    (f_val, hopper), node, g_val, path = q.get_nowait()
                    success = True
                    break
                except Empty:
                    continue
            print(f"Thread {tid} is working")

            if not success:
                empty_counter[tid] += 1
                if empty_counter[tid] > 100:
                    with done_lock:
                        thread_done[tid] = True
                        if all(thread_done):
                            stop_event.set()
                    return
                time.sleep(0.001)
                continue
            else:
                empty_counter[tid] = 0

            with best_goal_lock:
                if f_val > result['f_vec'][0]:
                    continue

            if visited.contains(node):
                continue
            visited.add(node)

            if node == goal:
                with best_goal_lock:
                    if f_val < result['f_vec'][0]:
                        result['path'] = path
                        result['f_vec'] = [f_val, hopper]
                stop_event.set()
                return

            for nbr in graph.neighbors(node):
                if not is_within_ellipse(nbr, start, goal, graph):
                    continue
                edge_cost = get_edge_cost(graph, node, nbr)
                tentative_g = g_val + edge_cost
                new_hop = hopper + 1

                print(f"Thread {tid} is working on node {node} with tentative g {tentative_g} and new hop {new_hop}")
                with g_lock:
                    if tentative_g > g_score[nbr]:
                        continue
                    if tentative_g == g_score[nbr] and new_hop >= result['f_vec'][1]:
                        continue
                    g_score[nbr] = tentative_g

                h_nbr = h_func(nbr, goal, graph)
                new_f = tentative_g + h_nbr
                open_queues[random.randint(0, num_threads - 1)].put(((new_f, new_hop), nbr, tentative_g, path + [nbr]))

    threads = [threading.Thread(target=worker, args=(i,), daemon=True) for i in range(num_threads)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    if result['path']:
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
    return None, None
