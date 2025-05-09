import os
import logging
import time
import osmnx as ox
import networkx as nx
from part3.algorithms import astar_parallel
from common.common import (
    load_map,
    load_point_pairs,
    dynamic_heuristic as dynamic_h,
    f_vector_basic,
    save_results,
    save_route_image
)

# --- Config ---
CITY = "Ho Chi Minh City"
POINT_FILE = "setup_points_list.env"
OUTPUT_BASE_DIR = "results"
THREAD_COUNTS = [1, 2, 4, 8, 12]
VERSIONS = ["fine", "optimistic"]

# --- Logger setup ---
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger()

# --- Benchmark wrapper ---
def run_astar(name, solver_func, graph, point_pairs, output_dir, image_dir, extra_args=None):
    results = []
    os.makedirs(image_dir, exist_ok=True)
    for (name1, coord1), (name2, coord2) in point_pairs:
        logger.info(f"{name}: Running {name1} → {name2}")
        try:
            node1 = ox.nearest_nodes(graph, coord1[1], coord1[0])
            node2 = ox.nearest_nodes(graph, coord2[1], coord2[0])
            start_time = time.time()
            path, f_vec = solver_func(node1, node2, graph, dynamic_h, f_vector_basic, **(extra_args or {}))
            elapsed = time.time() - start_time

            if path is None:
                distance = 0.0
                length = 0
            else:
                distance = nx.path_weight(graph, path, weight='length')
                length = len(path)
                save_route_image(graph, path, name1, name2, image_dir)

            results.append({
                "algo": name,
                "city": CITY,
                "start": name1,
                "goal": name2,
                "distance_m": round(distance, 2),
                "path_len": length,
                "f_score": round(f_vec[0], 3) if f_vec else 0.0,
                "extras": str(f_vec[1:]) if f_vec else "",
                "time_s": round(elapsed, 5)
            })
        except Exception as e:
            logger.warning(f"{name} failed on {name1} → {name2}: {e}")

    save_results(results, output_dir, f"benchmark_{name}")
    logger.info(f"Saved result to {output_dir}/benchmark_{name}.csv")

# --- Main Execution ---
if __name__ == "__main__":
    logger.info(f"Loading map for city: {CITY}")
    graph = load_map(CITY)
    point_pairs_by_city = load_point_pairs(POINT_FILE)
    if not isinstance(point_pairs_by_city, dict):
        raise TypeError("Expected a dictionary from load_point_pairs()")
    point_pairs = point_pairs_by_city.get(CITY, [])

    for version in VERSIONS:
        for threads in THREAD_COUNTS:
            algo_id = f"astar_parallel_{version}_{threads}t"
            run_dir = os.path.join(OUTPUT_BASE_DIR, "part3", f"{version}_{threads}t")
            img_dir = os.path.join(run_dir, "images")
            logger.info(f"Running: {algo_id}")
            run_astar(
                algo_id,
                astar_parallel,
                graph,
                point_pairs,
                run_dir,
                img_dir,
                {"version": version, "num_threads": threads}
            )
