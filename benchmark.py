import os
import importlib
import logging
import osmnx as ox
import time
import networkx as nx
import sys

# Fix import paths for part2 and part3 modules
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "part2")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "part3")))

from part1 import algorithms as part1_algorithms
from part3.algorithms import astar_solver as astar_parallel_solver
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
VERSIONS = ["fine_grain", "optimistic"]

# --- Logger setup ---
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
# logging.disable(logging.CRITICAL)
logger = logging.getLogger()

# --- Helper: run a single astar version ---
def run_astar_version(name, solver_func, graph, point_pairs, output_dir, image_dir, extra_args=None):
    results = []
    os.makedirs(image_dir, exist_ok=True)
    for (name1, coord1), (name2, coord2) in point_pairs:
        logger.info(f"{name}: Running {name1} → {name2}")
        try:
            node1 = ox.nearest_nodes(graph, coord1[1], coord1[0])
            node2 = ox.nearest_nodes(graph, coord2[1], coord2[0])
            start_time = time.time()
            if extra_args:
                path, f_vec = solver_func(node1, node2, graph, dynamic_h, f_vector_basic, logger=logger, **extra_args)
            else:
                path, f_vec = solver_func(node1, node2, graph, dynamic_h, f_vector_basic, logger=logger)
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
    logger.info(f"Saved result to {output_dir}\\benchmark_{name}.csv")

# --- Main Execution ---
if __name__ == "__main__":
    logger.info(f"Loading map for city: {CITY}")
    graph = load_map(CITY)
    point_pairs_by_city = load_point_pairs(POINT_FILE)
    if not isinstance(point_pairs_by_city, dict):
        raise TypeError("Expected a dictionary from load_point_pairs()")
    point_pairs = point_pairs_by_city.get(CITY, [])

    # Part 1: Sequential A*
    part1_dir = os.path.join(OUTPUT_BASE_DIR, "part1")
    part1_img = os.path.join(part1_dir, "images")
    logger.info("Running: part1.astar_sequential")
    run_astar_version("part1", part1_algorithms.astar_solver, graph, point_pairs, part1_dir, part1_img)

    # Part 3: Parallel A* with Fine-grained and Optimistic locks
    for version in VERSIONS:
        for threads in THREAD_COUNTS:
            algo_id = f"part3_{version}_{threads}t"
            run_dir = os.path.join(OUTPUT_BASE_DIR, "part3", f"run_with_{threads}_threads")
            img_dir = os.path.join(run_dir, "images")
            logger.info(f"Running: {algo_id}")
            run_astar_version(
                algo_id,
                astar_parallel_solver,
                graph,
                point_pairs,
                run_dir,
                img_dir,
                {"version": version, "num_threads": threads}
            )
