import threading
from queue import PriorityQueue
import queue
from concurrent.futures import ThreadPoolExecutor
from part2.fine_grained_lock import FineGrainedSet
from part2.optimistic_synchronization import OptimisticSet

def astar_solver(start, goal, map_data, h_func, f_vector_func, logger=None, version="fine_grain", num_threads=4):
    h0 = h_func(start, goal, map_data)
    f0 = f_vector_func(0, h0)
    if isinstance(f0, (float, int)):
        f0 = [f0, 0, h0]
    open_set = PriorityQueue()
    open_set.put((f0[0], f0, 0, start, [start]))

    if version == "fine_grain":
        lock = FineGrainedSet()
    elif version == "optimistic":
        lock = OptimisticSet()
    else:
        raise ValueError(f"Unsupported lock version: {version}")

    result = {"path": None, "f_vec": [float("inf"), float("inf"), float("inf")]}
    found = threading.Event()

    MAX_VISITS = 100000  # Ngăn vô hạn vòng lặp nếu graph quá lớn hoặc unreachable
    visit_counter = threading.local()

    def worker():
        visit_counter.count = 0

        while not found.is_set():
            if visit_counter.count > MAX_VISITS:
                if logger:
                    logger.warning(f"[Thread {threading.get_ident()}] Max visits reached ({MAX_VISITS}).")
                return

            try:
                _, f_vec, g, current, path = open_set.get_nowait()
            except queue.Empty:
                if logger:
                    logger.info(f"[Thread {threading.get_ident()}] Open set empty.")
                return

            visit_counter.count += 1

            logger.info(f"[Thread {threading.get_ident()}] Visiting: {current} with f={f_vec[0]}, g={f_vec[1]}, h={f_vec[2]}")

            if lock.contains(current):
                continue
            lock.add(current)

            if current == goal:
                result["path"] = path
                result["f_vec"] = f_vec
                found.set()
                logger.info(f"[Thread {threading.get_ident()}] Goal found!")
                return

            for neighbor in map_data.neighbors(current):
                try:
                    edge_data = map_data[current][neighbor][0]
                    if isinstance(edge_data, tuple):
                        edge_data = edge_data[2]
                    cost = edge_data.get('length', 1.0)
                except Exception as e:
                    if logger:
                        logger.warning(f"Edge access error: {current} → {neighbor}: {e}")
                    cost = 1.0

                if found.is_set():
                    return

                new_g = g + cost
                new_h = h_func(neighbor, goal, map_data)
                f_value = f_vector_func(new_g, new_h)
                if isinstance(f_value, (float, int)):
                    f_value = [f_value, new_g, new_h]

                open_set.put((f_value[0], f_value, new_g, neighbor, path + [neighbor]))

    # Sau ThreadPoolExecutor:
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [executor.submit(worker) for _ in range(num_threads)]
        for f in futures:
            f.result()

    if not found.is_set() and logger:
        logger.warning(f"A* did not find a path from {start} to {goal}")

    return result["path"], result["f_vec"]
