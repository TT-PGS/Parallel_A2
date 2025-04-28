import argparse
import time
import os
import osmnx as ox
from common import load_graph, nearest_node
from sequential_astar import astar_shortest_path
from parallel_astar import parallel_astar_linkedlist


def load_points(env_file="setup_points.env"):
    """Read start_point and end_point from .env file."""
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
    parser = argparse.ArgumentParser(
        description="A* pathfinding: sequential or parallel"
    )
    parser.add_argument(
        '--place', type=str, default="Ho Chi Minh City",
        help="Name of place to load graph"
    )
    parser.add_argument(
        '--parallel', nargs='?', const=4, type=int,
        help="Use parallel A*; optional number of cores (default 4)"
    )
    return parser.parse_args()


def main():
    args = parse_args()

    # Load start/end from env
    origin_coord, dest_coord = load_points()

    # Dynamic logger based on mode and coordinates
    def log(message):
        print(f"[LOG] {message}")
        mode = 'parallel' if args.parallel is not None else 'sequential'
        cores = args.parallel if args.parallel else ''
        orig = '_'.join(str(c) for c in origin_coord)
        dest = '_'.join(str(c) for c in dest_coord)
        suffix = f"_{cores}" if mode=='parallel' and cores else ''
        filename = f"{mode}_version{suffix}_{orig}_{dest}.txt"
        with open(filename, "a") as f:
            f.write(f"{message}\n")

    # Load graph and compute nodes
    graph = load_graph(args.place)
    origin_node = nearest_node(graph, origin_coord)
    destination_node = nearest_node(graph, dest_coord)

    # Run algorithm
    start = time.time()
    if args.parallel is not None:
        path, cost = parallel_astar_linkedlist(
            graph, origin_node, destination_node,
            max_workers=args.parallel
        )
        log(f"Parallel A* execution time: {time.time() - start:.2f}s")
    else:
        path, cost = astar_shortest_path(
            graph, origin_node, destination_node
        )
        log(f"Sequential A* execution time: {time.time() - start:.2f}s")

    # Log and plot
    if path:
        log(f"Path: {path[:5]}->...->{path[-1]}, cost={cost:.2f}")
        ox.plot_graph_route(graph, path, node_size=3)
    else:
        log("No path found.")

if __name__ == '__main__':
    main()