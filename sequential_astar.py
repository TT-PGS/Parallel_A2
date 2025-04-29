import heapq
import math
from common import euclidean_heuristic, speeds, log_common


def astar_shortest_path(graph, origin, destination,
                         heuristic=euclidean_heuristic):
    """Time-dependent A* shortest path (sequential)."""
    if origin not in graph or destination not in graph:
        # log_common("Origin or destination not in graph (sequential).")
        return None, None
    if origin == destination:
        return [origin], 0.0

    g_score = {origin: 0.0}
    h0 = heuristic(graph, origin, destination, 0.0)
    open_set = [(h0, 0.0, 0.0, origin, [origin])]
    closed = set()

    while open_set:
        f_cur, g_cur, t_cur, node, path = heapq.heappop(open_set)

        if node == destination:
            # log_common("Destination reached (sequential).")
            return path, g_cur

        if node in closed:
            continue
        closed.add(node)

        for nbr, data in graph[node].items():
            if nbr in closed:
                continue
            length = data.get('length', 1.0)
            speed = speeds[math.floor(t_cur) % len(speeds)]
            travel = length / speed
            t_next = t_cur + travel
            g_next = g_cur + travel
            if g_next < g_score.get(nbr, float('inf')):
                g_score[nbr] = g_next
                h_next = heuristic(graph, nbr, destination, t_next)
                f_next = g_next + h_next
                heapq.heappush(open_set,
                               (f_next, g_next, t_next, nbr, path + [nbr]))

    log_common("No path found (sequential).")
    return None, None