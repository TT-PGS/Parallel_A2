import heapq
import math

# Adjustable weights
WEIGHT_COST = 0.6
WEIGHT_HOP = 0.4

def get_edge_cost(graph, u, v):
    try:
        edge = graph[u][v][0]
        if isinstance(edge, tuple):
            edge = edge[2]
        return edge.get('length', 1.0)
    except Exception:
        return 1.0

def astar_solver(start_node, goal, graph, h_func, f_vector_func=None):
    """
    A* search with weighted scalar f = WEIGHT_COST * cost + WEIGHT_HOP * hop
    Returns: (path, [cost, hop]) or (None, None)
    """
    visited = {}  # node -> (g_cost, hopper)
    open_heap = []  # (f_weighted, node, g, hop, prev_dir, path)

    h0 = h_func(start_node, goal, graph)
    heapq.heappush(open_heap, (WEIGHT_COST * 0.0 + WEIGHT_HOP * 0, start_node, 0.0, 0, [start_node]))

    best_goal = None
    best_goal_score = (float('inf'), float('inf'))

    while open_heap:
        f_weighted, node, g_score_current_node, hop, path = heapq.heappop(open_heap)

        if node == goal:
            f_current = WEIGHT_COST * g_score_current_node + WEIGHT_HOP * hop
            f_best = WEIGHT_COST * best_goal_score[0] + WEIGHT_HOP * best_goal_score[1]
            if f_current < f_best:
                best_goal = (path, [g_score_current_node, hop])
                best_goal_score = (g_score_current_node, hop)
            continue

        if node in visited:
            old_g, old_hop = visited[node]
            if g_score_current_node > old_g:
                continue
            if g_score_current_node == old_g and hop >= old_hop:
                continue
        visited[node] = (g_score_current_node, hop)

        for neighbor_node in graph.neighbors(node):
            edge_cost = get_edge_cost(graph, node, neighbor_node)
            g_score_of_neighbor = g_score_current_node + edge_cost

            new_hop = hop + 1

            h_score_of_neighbor_node = h_func(neighbor_node, goal, graph)
            f_cost = g_score_of_neighbor + h_score_of_neighbor_node

            f_weighted = WEIGHT_COST * f_cost + WEIGHT_HOP * new_hop

            heapq.heappush(open_heap, (f_weighted, neighbor_node, g_score_of_neighbor, new_hop, path + [neighbor_node]))

    return best_goal if best_goal else (None, None)
