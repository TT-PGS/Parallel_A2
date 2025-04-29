// astar_multithread.cpp
#include <iostream>
#include <vector>
#include <queue>
#include <unordered_map>
#include <cmath>
#include <limits>
#include <tuple>
#include <chrono>
#include <thread>
#include <mutex>

// Simple Node structure
struct Node
{
    double x, y;
    std::vector<std::pair<int, double>> neighbors; // (neighbor_id, length)
};

std::unordered_map<int, Node> graph;
std::mutex open_set_mutex;
std::mutex g_score_mutex;

// Dummy graph for demo
void load_graph()
{
    // Graph: 0 --> 1 --> 2 --> 3 --> 4
    graph[0] = {0.0, 0.0, {{1, 1.0}}};
    graph[1] = {1.0, 0.0, {{2, 1.0}}};
    graph[2] = {2.0, 0.0, {{3, 1.0}}};
    graph[3] = {3.0, 0.0, {{4, 1.0}}};
    graph[4] = {4.0, 0.0, {}};
}

double heuristic(int node1, int node2)
{
    Node a = graph[node1];
    Node b = graph[node2];
    return std::sqrt((a.x - b.x) * (a.x - b.x) + (a.y - b.y) * (a.y - b.y));
}

void relax_neighbors(int current, int goal,
                     std::priority_queue<std::tuple<double, double, int>,
                                         std::vector<std::tuple<double, double, int>>,
                                         std::greater<>> &open_set,
                     std::unordered_map<int, double> &g_score)
{
    for (auto [neighbor, length] : graph[current].neighbors)
    {
        double tentative_g = g_score[current] + length;
        {
            std::lock_guard<std::mutex> lock(g_score_mutex);
            if (!g_score.count(neighbor) || tentative_g < g_score[neighbor])
            {
                g_score[neighbor] = tentative_g;
                double h = heuristic(neighbor, goal);
                {
                    std::lock_guard<std::mutex> lock2(open_set_mutex);
                    open_set.emplace(tentative_g + h, tentative_g, neighbor);
                }
            }
        }
    }
}

void astar_multithread(int start, int goal, int num_threads)
{
    std::priority_queue<std::tuple<double, double, int>,
                        std::vector<std::tuple<double, double, int>>,
                        std::greater<>>
        open_set;
    std::unordered_map<int, double> g_score;
    g_score[start] = 0.0;

    open_set.emplace(heuristic(start, goal), 0.0, start);

    while (!open_set.empty())
    {
        int batch_size = std::min(num_threads, (int)open_set.size());
        std::vector<std::thread> workers;
        std::vector<int> current_batch;

        {
            std::lock_guard<std::mutex> lock(open_set_mutex);
            for (int i = 0; i < batch_size; ++i)
            {
                auto [f, g, current] = open_set.top();
                open_set.pop();
                current_batch.push_back(current);
            }
        }

        for (int node : current_batch)
        {
            if (node == goal)
            {
                std::cout << "Reached goal!" << std::endl;
                return;
            }
            workers.emplace_back(relax_neighbors, node, goal, std::ref(open_set), std::ref(g_score));
        }

        for (auto &t : workers)
        {
            if (t.joinable())
                t.join();
        }
    }

    std::cout << "No path found" << std::endl;
}

int main(int argc, char *argv[])
{
    int num_threads = 4;
    if (argc > 1)
    {
        num_threads = std::stoi(argv[1]);
    }
    std::cout << "Running with " << num_threads << " threads\n";

    load_graph();
    auto start_time = std::chrono::steady_clock::now();

    astar_multithread(0, 4, num_threads); // tìm đường từ node 0 đến node 4

    auto end_time = std::chrono::steady_clock::now();
    auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(end_time - start_time);
    std::cout << "Elapsed time: " << duration.count() << "ms\n";
    return 0;
}
