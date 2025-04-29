import subprocess
import time
import statistics
import csv
import os
import pickle
import matplotlib.pyplot as plt

REPEAT = 2
THREAD_COUNTS = [4]
PROCESS_COUNTS = [3]

CSV_FILE = "benchmark_points_results.csv"
MARKDOWN_FILE = "benchmark_points_summary.md"

def load_points_list(env_file):
    pts = {}
    point_pairs = []
    with open(env_file, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if line.startswith('place='):
                pts['place'] = line.split('=', 1)[1].strip()
            elif line.startswith('point_pair='):
                val = line.split('=', 1)[1]
                start_str, end_str = val.split('->')
                start = tuple(map(float, start_str.strip().split(',')))
                end = tuple(map(float, end_str.strip().split(',')))
                point_pairs.append((start, end))
    return pts['place'], point_pairs

def preload_graph(place):
    import osmnx as ox
    filename = f"graph_{place.replace(' ', '_').replace(',', '')}.pkl"
    if os.path.exists(filename):
        print(f"✅ Loaded graph from {filename}")
        with open(filename, "rb") as f:
            graph = pickle.load(f)
    else:
        print(f"🔵 Downloading graph for {place}...")
        graph = ox.graph_from_place(place, network_type='drive')
        with open(filename, "wb") as f:
            pickle.dump(graph, f)
        print(f"✅ Saved graph to {filename}")
    return graph

def nearest_node(graph, point):
    import osmnx as ox
    lat, lon = point
    return ox.nearest_nodes(graph, lon, lat)

def run_command(command):
    start = time.time()
    subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    end = time.time()
    return end - start

def benchmark_mode(description, command):
    print(f"\nBenchmarking {description}...")
    times = []
    for i in range(REPEAT):
        print(f"  Run {i+1}/{REPEAT}...")
        elapsed = run_command(command)
        times.append(elapsed)
    avg_time = statistics.mean(times)
    print(f"→ {description} Average Time: {avg_time:.2f} seconds\n")
    return avg_time

def save_to_csv(all_results):
    with open(CSV_FILE, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Start", "End", "Mode", "Threads/Processes", "Average Time (seconds)"])
        for points, results in all_results.items():
            start, end = points
            for mode, data in results.items():
                for num, avg_time in data.items():
                    writer.writerow([start, end, mode, num if num else '-', avg_time])
    print(f"✅ Benchmark results saved to {CSV_FILE}")

def plot_results(all_results):
    for points, results in all_results.items():
        start, end = points
        plt.figure(figsize=(12, 7))
        for mode, data in results.items():
            counts = list(data.keys())
            times = list(data.values())
            plt.plot(counts, times, marker='o', label=mode)
        plt.title(f'Benchmark: {start} -> {end}')
        plt.xlabel('Threads/Processes')
        plt.ylabel('Average Time (seconds)')
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.legend()
        plt.tight_layout()
        filename = f"benchmark_{start[0]:.4f}_{start[1]:.4f}_to_{end[0]:.4f}_{end[1]:.4f}.png".replace('.', '_')
        plt.savefig(filename)
        plt.close()
        print(f"✅ Plot saved for {start}->{end}")

def generate_markdown(all_results):
    md_lines = []
    md_lines.append("# 📋 Benchmark Summary (Points)\n")
    md_lines.append("| Start | End | Mode | Threads/Processes | Average Time (seconds) |")
    md_lines.append("|:--|:--|:--|:--|:--|")

    for points, results in all_results.items():
        start, end = points
        for mode, data in results.items():
            for num, avg_time in data.items():
                md_lines.append(f"| {start} | {end} | {mode} | {num if num else '-'} | {avg_time:.2f} |")

    markdown_text = "\n".join(md_lines)

    with open(MARKDOWN_FILE, "w", encoding="utf-8") as f:
        f.write(markdown_text)

    print("✅ Benchmark summary saved as 'benchmark_points_summary.md'")

def main():
    print("="*40)
    print("🚀 Benchmark Multiple Points in 1 City")
    print("="*40)

    setup_file = "setup_points_list.env"
    place, point_pairs = load_points_list(setup_file)
    graph = preload_graph(place)

    all_results = {}

    for start_point, end_point in point_pairs:
        print(f"\n🏁 Start: {start_point} -> 🏁 End: {end_point}")
        origin_node = nearest_node(graph, start_point)
        destination_node = nearest_node(graph, end_point)

        results = {}

        results['Python Sequential'] = {0: benchmark_mode("Python Sequential", "python main.py")}
        results['Python Multi-thread'] = {n: benchmark_mode(f"Python Multi-thread ({n})", f"python main.py -n {n}") for n in THREAD_COUNTS}
        results['Python Multi-process'] = {m: benchmark_mode(f"Python Multi-process ({m})", f"python main.py -m {m}") for m in PROCESS_COUNTS}

        results['C++ Sequential'] = {0: benchmark_mode("C++ Sequential", "./astar_sequential_cpp")}
        results['C++ Multi-thread'] = {n: benchmark_mode(f"C++ Multi-thread ({n})", f"./astar_multithread_cpp {n}") for n in THREAD_COUNTS}
        results['C++ OpenMP'] = {n: benchmark_mode(f"C++ OpenMP ({n})", f"./astar_openmp_cpp {n}") for n in THREAD_COUNTS}

        all_results[(start_point, end_point)] = results

    save_to_csv(all_results)
    plot_results(all_results)
    generate_markdown(all_results)

    print("="*40)
    print("✅ All Points Benchmark Completed")
    print("="*40)

if __name__ == "__main__":
    main()
