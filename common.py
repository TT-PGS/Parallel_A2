import os
import time
import math
import osmnx as ox
import networkx as nx

# Speeds (meters per minute) over time steps
speeds = [350, 350, 500, 500, 600, 600, 550, 500, 400, 300,
          600, 550, 500, 400, 300, 600, 550, 500, 400, 300]


def log_common(message):
    """Generic log for common utilities (writes to common.txt)."""
    print(f"[LOG] {message}")
    script = os.path.splitext(os.path.basename(__file__))[0]
    filename = f"{script}.txt"
    with open(filename, "a") as f:
        f.write(f"{message}\n")


def euclidean_heuristic(graph, n1, n2, t=0):
    """Euclidean distance divided by speed as heuristic."""
    p1 = graph.nodes[n1]
    p2 = graph.nodes[n2]
    dx = p1['x'] - p2['x']
    dy = p1['y'] - p2['y']
    dist = math.hypot(dx, dy)
    speed = speeds[math.floor(t) % len(speeds)]
    return dist / speed


def load_graph(place):
    """Load and return a drive network graph for the given place."""
    log_common(f"Loading graph for {place}...")
    return ox.graph_from_place(place, network_type="drive")


def nearest_node(graph, point):
    """Return nearest node for (latitude, longitude)."""
    lat, lon = point
    return ox.nearest_nodes(graph, lon, lat)