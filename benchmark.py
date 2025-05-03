import time
import csv
import os
from common.common import load_map, load_point_pairs, setup_logger
from part1.algorithms import astar_serial

def dynamic_h(node, goal, map_data):
    return ((node[0] - goal[0]) ** 2 + (node[1] - goal[1]) ** 2) ** 0.5

def extra1(node, goal, map_data, g_cost):
    return g_cost / 2

def extra2(node, goal, map_data, g_cost):
    return abs(node[0] - goal[0]) + abs(node[1] - goal[1])  # Manhattan distance

def run_serial_benchmark(point_file, output_csv='benchmark_part1.csv', log_file=None):
    logger = setup_logger(log_file)
    pairs_by_city = load_point_pairs(point_file)
    results = []

    for city, pairs in pairs_by_city.items():
        map_data = load_map(city)
        logger.info(f"Loaded map for {city} with {len(pairs)} point pairs")

        for start, goal in pairs:
            t0 = time.time()
            path, f_vec = astar_serial(start, goal, map_data, dynamic_h, [extra1, extra2], logger)
            elapsed = time.time() - t0
            results.append({
                'city': city,
                'start': start,
                'goal': goal,
                'path_len': len(path) if path else 0,
                'f_vector': f_vec,
                'time_s': elapsed
            })

    with open(output_csv, 'w', newline='') as csvfile:
        fieldnames = ['city', 'start', 'goal', 'path_len', 'f_vector', 'time_s']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in results:
            writer.writerow(row)

    logger.info(f"Benchmark complete. Results saved to {output_csv}")

if __name__ == '__main__':
    run_serial_benchmark('setup_points_list.env')