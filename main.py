import argparse
import time
import osmnx as ox
from common import load_graph, nearest_node, log
from sequential_astar import astar_shortest_path
from parallel_astar import parallel_astar_linkedlist


def parse_args():
    parser = argparse.ArgumentParser(
        description="A* pathfinding: sequential or parallel"
    )
    parser.add_argument(
        '--place', type=str, default="Ho Chi Minh City",
        help="Name of place to load graph"
    )
    parser.add_argument(
        '--origin', type=float, nargs=2,
        default=[10.768856, 106.725019],
        metavar=('LAT','LON'),
        help="Origin coordinates: latitude longitude"
    )
    parser.add_argument(
        '--destination', type=float, nargs=2,
        default=[10.839613, 106.845798],
        metavar=('LAT','LON'),
        help="Destination coordinates: latitude longitude"
    )
    parser.add_argument(
        '--parallel', action='store_true',
        help="Use parallel A* algorithm"
    )
    parser.add_argument(
        '--workers', type=int, default=4,
        help="Number of threads for parallel A*"
    )
    return parser.parse_args()


def main():
    args = parse_args()
    graph = load_graph(args.place)
    origin_node = nearest_node(graph, args.origin)
    destination_node = nearest_node(graph, args.destination)

    start = time.time()
    if args.parallel:
        path, cost = parallel_astar_linkedlist(
            graph, origin_node, destination_node,
            max_workers=args.workers
        )
    else:
        path, cost = astar_shortest_path(
            graph, origin_node, destination_node
        )
    elapsed = time.time() - start
    log(f"Execution time: {elapsed:.2f}s")
    if path:
        log(f"Path found: {path[:5]} -> ... -> {path[-1]}, time={cost:.2f}")
        ox.plot_graph_route(graph, path, node_size=3)
    else:
        log("No path found.")

if __name__ == '__main__':
    main()
