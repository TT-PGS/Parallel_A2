import argparse
import time
import os
import osmnx as ox
from common import load_graph, nearest_node
from sequential_astar import astar_shortest_path
from parallel_astar import parallel_astar_linkedlist
from multiprocessing_astar import multiprocessing_astar

def load_points(env_file="setup_points.env"):
    pts = {}
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            key, val = line.split('=', 1)
            pts[key.strip()] = tuple(map(float, val.split(',')))
    return pts['start_point'], pts['end_point']

def parse_args():
    parser = argparse.ArgumentParser(description="A* pathfinding: sequential / multi-thread / multi-process")
    parser.add_argument('-n', nargs='?', const=4, type=int,
                        help="Run in multi-thread mode (optional number of threads, default=4)")
    parser.add_argument('-m', nargs='?', const=3, type=int,
                        help="Run in multi-process mode (optional number of processes, default=3)")
    return parser.parse_args()

def main():
    args = parse_args()

    origin_coord, dest_coord = load_points()

    def log(message):
        print(f"[LOG] {message}")
        if args.n is not None:
            mode = 'multithread'
            cores = args.n
        elif args.m is not None:
            mode = 'multiprocess'
            cores = args.m
        else:
            mode = 'sequential'
            cores = ''
        orig = '_'.join(str(c) for c in origin_coord)
        dest = '_'.join(str(c) for c in dest_coord)
        suffix = f"_{cores}" if cores else ''
        filename = f"{mode}_version{suffix}_{orig}_{dest}.txt"
        with open(filename, "a") as f:
            f.write(f"{message}\n")

    graph = load_graph("Ho Chi Minh City")
    origin_node = nearest_node(graph, origin_coord)
    destination_node = nearest_node(graph, dest_coord)

    start = time.time()
    if args.n is not None:
        path, cost = parallel_astar_linkedlist(graph, origin_node, destination_node, max_workers=args.n)
        log(f"Multi-thread A* execution time: {time.time() - start:.2f}s")
    elif args.m is not None:
        path, cost = multiprocessing_astar(graph, origin_node, destination_node, num_workers=args.m)
        log(f"Multi-process A* execution time: {time.time() - start:.2f}s")
    else:
        path, cost = astar_shortest_path(graph, origin_node, destination_node)
        log(f"Sequential A* execution time: {time.time() - start:.2f}s")

    if path:
        log(f"Path found: {path[:5]} -> ... -> {path[-1]}, cost={cost:.2f}")
        # ox.plot_graph_route(graph, path, node_size=3)
    else:
        log("No path found.")

if __name__ == '__main__':
    main()
