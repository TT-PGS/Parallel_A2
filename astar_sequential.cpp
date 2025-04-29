// astar_sequential.cpp
#include <iostream>
#include <vector>
#include <queue>
#include <unordered_map>
#include <cmath>
#include <limits>
#include <tuple>
#include <chrono>

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
    // 0 --> 1 --> 2
    graph[0] = {0.0, 0.0, {{1, 1.0}}};
    graph[1] = {1.0, 0.0, {{2, 1.0}}};
    graph[2] = {2.0, 0.0, {}};
}

double heuristic(int node1, int node2)
{
    Node a = graph[node1];
    Node b = graph[node2];
    return std::sqrt((a.x - b.x) * (a.x - b.x) + (a.y - b.y) * (a.y - b.y));
}

void astar(int start, int goal)
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
        auto [f, g, current] = open_set.top();
        open_set.pop();

        if (current == goal)
        {
            std::cout << "Reached goal with cost " << g << "\\n";
            return;
        }

        for (auto [neighbor, length] : graph[current].neighbors)
        {
            double tentative_g = g + length;
            if (!g_score.count(neighbor) || tentative_g < g_score[neighbor])
            {
                g_score[neighbor] = tentative_g;
                double h = heuristic(neighbor, goal);
                open_set.emplace(tentative_g + h, tentative_g, neighbor);
            }
        }
    }
    std::cout << "No path found\\n";
}

int main()
{
    load_graph();
    auto start_time = std::chrono::steady_clock::now();

    astar(0, 2); // tìm đường từ node 0 đến node 2

    auto end_time = std::chrono::steady_clock::now();
    auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(end_time - start_time);
    std::cout << "Elapsed time: " << duration.count() << "ms\\n";
    return 0;
}
