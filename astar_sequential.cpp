#include <iostream>
#include <vector>
#include <queue>
#include <unordered_map>
#include <cmath>
#include <limits>
#include <utility>
#include <algorithm>

struct Edge
{
    int to;
    double cost;
};
typedef std::unordered_map<int, std::vector<Edge>> Graph;
typedef std::unordered_map<int, std::pair<double, double>> Coords;

struct PQItem
{
    double f, g;
    int id;
    PQItem(double _f, double _g, int _id)
        : f(_f), g(_g), id(_id) {}
};

struct ComparePQ
{
    bool operator()(PQItem const &a, PQItem const &b) const
    {
        return a.f > b.f;
    }
};

double heuristic(int u, int v, Coords const &coords)
{
    double xu = coords.at(u).first;
    double yu = coords.at(u).second;
    double xv = coords.at(v).first;
    double yv = coords.at(v).second;
    return std::hypot(xu - xv, yu - yv);
}

std::vector<int> astar(Graph const &graph, int start, int goal, Coords const &coords)
{
    std::priority_queue<PQItem, std::vector<PQItem>, ComparePQ> open_set;
    struct Node
    {
        double g;
        int parent;
    };
    std::unordered_map<int, Node> closed;

    double h0 = heuristic(start, goal, coords);
    open_set.push(PQItem(h0, 0.0, start));
    closed[start] = Node{0.0, -1};

    while (!open_set.empty())
    {
        PQItem top = open_set.top();
        open_set.pop();
        int u = top.id;
        double g = top.g;
        if (u == goal)
            break;
        if (g > closed[u].g)
            continue;

        std::vector<Edge> const &nbr = graph.at(u);
        for (size_t i = 0; i < nbr.size(); ++i)
        {
            int v = nbr[i].to;
            double ng = g + nbr[i].cost;
            if (closed.find(v) == closed.end() || ng < closed[v].g)
            {
                double h = heuristic(v, goal, coords);
                open_set.push(PQItem(ng + h, ng, v));
                closed[v] = Node{ng, u};
            }
        }
    }

    std::vector<int> path;
    if (!closed.count(goal))
        return path;
    for (int cur = goal; cur != -1; cur = closed[cur].parent)
        path.push_back(cur);
    std::reverse(path.begin(), path.end());
    return path;
}

int main()
{
    Graph graph;
    Coords coords;

    graph[0] = std::vector<Edge>{{1, 1.0}, {2, 2.0}};
    graph[1] = std::vector<Edge>{{2, 1.0}};
    coords[0] = std::make_pair(0.0, 0.0);
    coords[1] = std::make_pair(1.0, 0.0);
    coords[2] = std::make_pair(2.0, 0.0);

    std::vector<int> path = astar(graph, 0, 2, coords);
    std::cout << "Path:";
    for (size_t i = 0; i < path.size(); ++i)
        std::cout << " " << path[i];
    std::cout << std::endl;
    return 0;
}
