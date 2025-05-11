import os
import unittest
import osmnx as ox
import networkx as nx
import time

from part3.algorithms import astar_parallel as astar_parallel_solver
from common.common import (
    load_map,
    load_point_pairs,
    dynamic_heuristic as dynamic_h,
    f_vector_basic,
    save_results,
    save_route_image
)

CITY = "Ho Chi Minh City"
POINT_FILE = "setup_points_list.env"
OUTPUT_BASE_DIR = "results"
THREAD_COUNTS = [1, 2, 4, 8, 12]
VERSIONS = ["FineGrain", "Optimictis"]

class TestParallelAStar(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.graph = load_map(CITY)
        point_pairs_by_city = load_point_pairs(POINT_FILE)
        cls.point_pairs = point_pairs_by_city.get(CITY, [])
        os.makedirs(OUTPUT_BASE_DIR, exist_ok=True)

    def run_astar_version(self, name, version, threads):
        results = []
        image_dir = os.path.join(OUTPUT_BASE_DIR, "part3",
                                 f"run_with_{threads}_threads", "images")
        os.makedirs(image_dir, exist_ok=True)

        for (name1, coord1), (name2, coord2) in self.point_pairs:
            node1 = ox.nearest_nodes(self.graph, coord1[1], coord1[0])
            node2 = ox.nearest_nodes(self.graph, coord2[1], coord2[0])
            start_time = time.time()
            path, f_vec = astar_parallel_solver(
                node1, node2, self.graph,
                dynamic_h, f_vector_basic,
                version=version, num_threads=threads
            )
            elapsed = time.time() - start_time

            if path:
                distance = nx.path_weight(self.graph, path, weight='length')
                length = len(path)
                save_route_image(self.graph, path, name1, name2, image_dir)
            else:
                distance = 0.0
                length = 0

            f_cost = round(f_vec[0], 3) if f_vec else 0.0
            hopper = int(f_vec[1]) if f_vec and len(f_vec) > 1 else 0

            results.append({
                "algo": "astar_hopper",
                "city": CITY,
                "start": name1,
                "goal": name2,
                "distance_m": round(distance, 2),
                "path_len": length,
                "f_cost": f_cost,
                "hopper": hopper,
                "time_s": round(elapsed, 5)
            })

        result_dir = os.path.join(OUTPUT_BASE_DIR, "part3", f"run_with_{threads}_threads_and_{version}")
        os.makedirs(result_dir, exist_ok=True)  # ✅ Sửa lỗi thiếu thư mục
        save_results(results, result_dir, f"benchmark_astar_hopper")

    def test_parallel_astar(self):
        for version in VERSIONS:
            for threads in THREAD_COUNTS:
                self.run_astar_version("astar_hopper", version, threads)

if __name__ == "__main__":
    unittest.main()
