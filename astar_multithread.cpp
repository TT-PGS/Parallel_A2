#include <iostream>
#include <vector>
#include <queue>
#include <unordered_map>
#include <cmath>
#include <limits>
#include <thread>
#include <mutex>
#include <condition_variable>
#include <algorithm>
#include <utility>

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

std::mutex mtx;
std::condition_variable cv;
bool done_flag;

void worker(const Graph &graph,
            int goal,
            Coords const &coords,
            std::priority_queue<PQItem, std::vector<PQItem>, ComparePQ> &open_set,
            std::unordered_map<int, std::pair<double, int>> &closed)
{
    while (true)
    {
        PQItem item(0, 0, 0);
        {
            std::unique_lock<std::mutex> lk(mtx);
            cv.wait(lk, [&open_set]
                    { return done_flag || !open_set.empty(); });
            if (done_flag && open_set.empty())
                return;
            item = open_set.top();
            open_set.pop();
        }

        int u = item.id;
        double g = item.g;
        if (u == goal)
        {
            {
                std::lock_guard<std::mutex> lk(mtx);
                done_flag = true;
            }
            cv.notify_all();
            return;
        }

        {
            std::lock_guard<std::mutex> lk(mtx);
            if (g > closed[u].first)
                continue;
        }

        std::vector<Edge> const &nbr = graph.at(u);
        for (size_t i = 0; i < nbr.size(); ++i)
        {
            int v = nbr[i].to;
            double ng = g + nbr[i].cost;
            std::unique_lock<std::mutex> lk(mtx);
            if (closed.find(v) == closed.end() || ng < closed[v].first)
            {
                closed[v] = std::make_pair(ng, u);
                double f = ng + heuristic(v, goal, coords);
                open_set.push(PQItem(f, ng, v));
                cv.notify_one();
            }
        }
    }
}

std::vector<int> astar_mt(const Graph &graph,
                          int start, int goal, Coords const &coords, int num_threads)
{
    std::priority_queue<PQItem, std::vector<PQItem>, ComparePQ> open_set;
    std::unordered_map<int, std::pair<double, int>> closed;

    double h0 = heuristic(start, goal, coords);
    open_set.push(PQItem(h0, 0.0, start));
    closed[start] = std::make_pair(0.0, -1);
    done_flag = false;

    std::vector<std::thread> threads;
    for (int i = 0; i < num_threads; ++i)
        threads.emplace_back(worker,
                             std::cref(graph), goal, std::cref(coords),
                             std::ref(open_set), std::ref(closed));

    {
        std::lock_guard<std::mutex> lk(mtx);
        cv.notify_all();
    }
    for (auto &t : threads)
        t.join();

    std::vector<int> path;
    if (!closed.count(goal))
        return path;
    for (int cur = goal; cur != -1; cur = closed[cur].second)
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

    std::vector<int> path = astar_mt(graph, 0, 2, coords, 4);
    std::cout << "MT Path:";
    for (size_t i = 0; i < path.size(); ++i)
        std::cout << " " << path[i];
    std::cout << std::endl;
    return 0;
}
