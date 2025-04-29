// astar_openmp.cpp
#include <iostream>
#include <vector>
#include <queue>
#include <unordered_map>
#include <cmath>
#include <limits>
#include <tuple>
#include <chrono>
#include <omp.h>

// Simple Node structure
struct Node
{
    double x, y;
    std::vector<std::pair<int, double>> neighbors; // (neighbor_id, length)
};

std::unordered_map<int, Node> graph;

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

void astar_openmp(int start, int goal, int num_threads)
{
    std::priority_queue<std::tuple<double, double, int>,
                        std::vector<std::tuple<double, double, int>>,
                        std::greater<>>
        open_set;
    std::unordered_map<int, double> g_score;
    g_score[start] = 0.0;

    open_set.emplace(heuristic(start, goal), 0.0, start);

    omp_set_num_threads(num_threads);

    while (!open_set.empty())
    {
        int batch_size = std::min(num_threads, (int)open_set.size());
        std::vector<std::tuple<double, double, int>> batch;

        for (int i = 0; i < batch_size; ++i)
        {
            auto [f, g, current] = open_set.top();
            open_set.pop();
            batch.emplace_back(f, g, current);
        }

        bool goal_found = false;
#pragma omp parallel for shared(goal_found)
        for (int i = 0; i < batch.size(); ++i)
        {
            auto [f, g, current] = batch[i];

            if (current == goal)
            {
#pragma omp critical
                {
                    goal_found = true;
                }
            }

            for (auto [neighbor, length] : graph[current].neighbors)
            {
                double tentative_g = g + length;

#pragma omp critical
                {
                    if (!g_score.count(neighbor) || tentative_g < g_score[neighbor])
                    {
                        g_score[neighbor] = tentative_g;
                        double h = heuristic(neighbor, goal);
                        open_set.emplace(tentative_g + h, tentative_g, neighbor);
                    }
                }
            }
        }

        if (goal_found)
        {
            std::cout << "Reached goal!\n";
            return;
        }
    }

    std::cout << "No path found\n";
}

int main(int argc, char *argv[])
{
    int num_threads = 4;
    if (argc > 1)
    {
        num_threads = std::stoi(argv[1]);
    }
    std::cout << "Running with " << num_threads << " threads (OpenMP)\n";

    load_graph();
    auto start_time = std::chrono::steady_clock::now();

    astar_openmp(0, 4, num_threads);

    auto end_time = std::chrono::steady_clock::now();
    auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(end_time - start_time);
    std::cout << "Elapsed time: " << duration.count() << "ms\n";
    return 0;
}
