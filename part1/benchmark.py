import os
import time
import math
import logging
import osmnx as ox
import networkx as nx

from part1.algorithms import astar_solver  # sửa thành đúng module
from common.common import (
    load_map,
    load_point_pairs,
    save_results,
    save_route_image
)

CITY = "Ho Chi Minh City"
POINT_FILE = "setup_points_list.env"
OUTPUT_DIR = "results/part1"
IMG_DIR = os.path.join(OUTPUT_DIR, "images")

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger()

def euclidean_h(u, v, g):
    x1, y1 = g.nodes[u]['x'], g.nodes[u]['y']
    x2, y2 = g.nodes[v]['x'], g.nodes[v]['y']
    return math.hypot(x2 - x1, y2 - y1)

def run_benchmark():
    graph = load_map(CITY)
    point_pairs = load_point_pairs(POINT_FILE).get(CITY, [])

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(IMG_DIR, exist_ok=True)
    results = []

    for (p1_name, p1_coord), (p2_name, p2_coord) in point_pairs:
        logger.info(f"A* Hopper: {p1_name} → {p2_name}")
        try:
            u = ox.nearest_nodes(graph, p1_coord[1], p1_coord[0])
            v = ox.nearest_nodes(graph, p2_coord[1], p2_coord[0])

            t0 = time.time()
            path, fvec = astar_solver(u, v, graph, euclidean_h)
            t1 = time.time()

            if path is None:
                distance = 0.0
                length = 0
                f = 0
                h = 0
            else:
                distance = nx.path_weight(graph, path, weight='length')
                length = len(path)
                f = fvec[0]
                h = fvec[1]
                save_route_image(graph, path, p1_name, p2_name, IMG_DIR)

            results.append({
                "algo": "astar_hopper",
                "city": CITY,
                "start": p1_name,
                "goal": p2_name,
                "distance_m": round(distance, 2),
                "path_len": length,
                "f_cost": round(f, 3),
                "hopper": h,
                "time_s": round(t1 - t0, 5)
            })

        except Exception as e:
            logger.warning(f"Failed on {p1_name} → {p2_name}: {e}")

    save_results(results, OUTPUT_DIR, "benchmark_astar_hopper")
    logger.info("Benchmark complete.")

if __name__ == "__main__":
    run_benchmark()
