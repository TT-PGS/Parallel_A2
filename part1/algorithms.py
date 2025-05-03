import heapq

def astar_solver(start, goal, map_data, h_func, f_vector_func, logger=None):
    g_costs = {start: 0}
    came_from = {}
    h0 = h_func(start, goal, map_data)
    extras0 = f_vector_func(0, h0)
    f0 = (0 + h0, *extras0)
    open_set = []
    heapq.heappush(open_set, (f0, start))
    closed = set()

    while open_set:
        current_f, current = heapq.heappop(open_set)
        if current == goal:
            path = []
            node = current
            while node in came_from:
                path.append(node)
                node = came_from[node]
            path.append(start)
            path.reverse()
            return path, current_f

        if current in closed:
            continue
        closed.add(current)

        for neighbor in map_data.neighbors(current):
            try:
                edge_data = map_data[current][neighbor][0]  # get edge attributes
                cost = edge_data.get('length', 1.0)
            except Exception as e:
                if logger:
                    logger.warning(f"Missing edge data between {current} and {neighbor}: {e}")
                cost = 1.0  # fallback

            tentative_g = g_costs[current] + cost
            if neighbor not in g_costs or tentative_g < g_costs[neighbor]:
                g_costs[neighbor] = tentative_g
                came_from[neighbor] = current
                h_val = h_func(neighbor, goal, map_data)
                extras = f_vector_func(tentative_g, h_val)
                f_vec = (tentative_g + h_val, *extras)
                heapq.heappush(open_set, (f_vec, neighbor))
                if logger:
                    logger.debug(f"Visiting {neighbor}, g={tentative_g}, f_vec={f_vec}")

    return None, None
