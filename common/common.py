import os
import pickle
import logging
import osmnx as ox
import networkx as nx

# --- Config ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SETUP_DIR = os.path.join(BASE_DIR, '..', 'setup')
MAPS_DIR = os.path.join(SETUP_DIR, 'maps')
POINTS_DIR = os.path.join(SETUP_DIR, 'points')

# ----------------------- Heuristics & Scoring -----------------------
def dynamic_heuristic(node, goal, graph, t=0.0):
    """Heuristic based on Euclidean distance divided by time-varying speed."""
    x1, y1 = graph.nodes[node]['x'], graph.nodes[node]['y']
    x2, y2 = graph.nodes[goal]['x'], graph.nodes[goal]['y']
    dx, dy = x1 - x2, y1 - y2
    distance = (dx ** 2 + dy ** 2) ** 0.5
    speeds = [350, 350, 500, 500, 600, 600, 550, 500, 400, 300,
              600, 550, 500, 400, 300, 600, 550, 500, 400, 300]
    speed = speeds[int(t) % len(speeds)]
    return distance / speed

def f_vector_basic(g_score, h_score, hopper_count, t=0.0):
    """Basic f-vector function."""
    f_score = g_score + h_score
    WEIGHT_COST = 0.6
    WEIGHT_HOP = 0.4
    f_weight = WEIGHT_COST * f_score + WEIGHT_HOP * hopper_count
    return (f_weight, hopper_count, t)

# --------------------------- I/O Handling ---------------------------
def ensure_setup_dirs():
    if not os.path.isdir(POINTS_DIR):
        raise FileNotFoundError(f"Required directory not found: {POINTS_DIR}")
    os.makedirs(MAPS_DIR, exist_ok=True)

def _original_load_map(city_name: str):
    print(f"📅 Downloading map for '{city_name}' from OSM...")
    graph = ox.graph_from_place(city_name, network_type='drive', simplify=True)
    return graph

def load_map(city_name: str):
    ensure_setup_dirs()
    pkl_path = os.path.join(MAPS_DIR, f"{city_name}.pkl")
    if os.path.isfile(pkl_path):
        with open(pkl_path, 'rb') as f:
            return pickle.load(f)
    graph = _original_load_map(city_name)
    with open(pkl_path, 'wb') as f:
        pickle.dump(graph, f)
    return graph

def load_point_pairs(file_name):
    ensure_setup_dirs()
    file_path = os.path.join(POINTS_DIR, file_name)
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"Point file not found: {file_path}")

    pairs_by_city = {}
    current_city = None

    with open(file_path, 'r', encoding='utf-8') as f:
        for idx, line in enumerate(f, start=1):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if line.startswith('place='):
                current_city = line.split('=', 1)[1].strip()
                pairs_by_city[current_city] = []
            elif line.startswith('point_pair='):
                if current_city is None:
                    raise ValueError(f"City must be defined before point pairs (line {idx})")
                try:
                    pair_str = line.split('=', 1)[1].strip()
                    coords = pair_str.split('->')
                    name1, lat1, lon1 = coords[0].strip().split(',')
                    name2, lat2, lon2 = coords[1].strip().split(',')
                    pairs_by_city[current_city].append(((name1.strip(), (float(lat1), float(lon1))),
                                                         (name2.strip(), (float(lat2), float(lon2))))
                                                      )
                except Exception as e:
                    raise ValueError(f"Invalid point_pair format on line {idx}: {line}\n{e}")
    return pairs_by_city

def save_results_csv(results, file_path):
    with open(file_path, 'w', encoding='utf-8') as f:
        headers = results[0].keys() if results else []
        f.write(','.join(headers) + '\n')
        for r in results:
            f.write(','.join(str(r[k]) for k in headers) + '\n')

def save_results_md(results, file_path):
    with open(file_path, 'w', encoding='utf-8') as f:
        if results:
            headers = results[0].keys()
            f.write('| ' + ' | '.join(headers) + ' |\n')
            f.write('| ' + ' | '.join(['---'] * len(headers)) + ' |\n')
            for r in results:
                f.write('| ' + ' | '.join(str(r[k]) for k in headers) + ' |\n')

def save_results(results, out_dir, file_prefix):
    save_results_csv(results, os.path.join(out_dir, f"{file_prefix}.csv"))
    save_results_md(results, os.path.join(out_dir, f"{file_prefix}.md"))

def save_route_image(graph, path, name1, name2, image_dir):
    os.makedirs(image_dir, exist_ok=True)
    fig, ax = ox.plot_graph_route(graph, path, node_size=3, show=False, close=True)
    filename = f"{name1.replace(' ', '_')}_TO_{name2.replace(' ', '_')}.png"
    fig.savefig(os.path.join(image_dir, filename))

def setup_logger(log_file=None, level=logging.INFO):
    logger = logging.getLogger('astar_bench')
    if not logger.handlers:
        handler = logging.FileHandler(log_file, encoding='utf-8') if log_file else logging.StreamHandler()
        fmt = '%(asctime)s - %(levelname)s - %(message)s'
        handler.setFormatter(logging.Formatter(fmt))
        logger.addHandler(handler)
    logger.setLevel(level)
    return logger
