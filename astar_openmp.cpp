#include <mpi.h>
#include <iostream>
#include <vector>
#include <queue>
#include <unordered_map>
#include <cmath>
#include <limits>
#include <utility>

struct Edge
{
    int to;
    double cost;
};
typedef std::unordered_map<int, std::vector<Edge>> Graph;
typedef std::unordered_map<int, std::pair<double, double>> Coords;

double heuristic(int u, int v, Coords const &coords)
{
    double xu = coords.at(u).first;
    double yu = coords.at(u).second;
    double xv = coords.at(v).first;
    double yv = coords.at(v).second;
    return std::hypot(xu - xv, yu - yv);
}

double astar_dist(const Graph &graph, int start, int goal, Coords const &coords)
{
    struct Item
    {
        int id;
        double f;
        double g;
        int parent;
    };
    struct Cmp
    {
        bool operator()(Item const &a, Item const &b) const
        {
            return a.f > b.f;
        }
    };

    std::priority_queue<Item, std::vector<Item>, Cmp> open;
    std::unordered_map<int, double> best_g;
    best_g[start] = 0.0;
    open.push(Item{start, heuristic(start, goal, coords), 0.0, -1});

    while (!open.empty())
    {
        Item cur = open.top();
        open.pop();
        int u = cur.id;
        double g = cur.g;
        if (u == goal)
            return g;
        if (g > best_g[u])
            continue;

        std::vector<Edge> const &nbr = graph.at(u);
        for (size_t i = 0; i < nbr.size(); ++i)
        {
            int v = nbr[i].to;
            double g2 = g + nbr[i].cost;
            if (best_g.find(v) == best_g.end() || g2 < best_g[v])
            {
                best_g[v] = g2;
                double f2 = g2 + heuristic(v, goal, coords);
                open.push(Item{v, f2, g2, u});
            }
        }
    }
    return std::numeric_limits<double>::infinity();
}

int main(int argc, char **argv)
{
    MPI_Init(&argc, &argv);
    int rank, nprocs;
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &nprocs);

    Graph graph;
    Coords coords;
    graph[0] = std::vector<Edge>{{1, 1.0}, {2, 2.0}};
    graph[1] = std::vector<Edge>{{2, 1.0}};
    coords[0] = std::make_pair(0.0, 0.0);
    coords[1] = std::make_pair(1.0, 0.0);
    coords[2] = std::make_pair(2.0, 0.0);

    double dist = astar_dist(graph, 0, 2, coords);

    std::vector<double> all_dists;
    if (rank == 0)
        all_dists.resize(nprocs);
    double *recvbuf = (rank == 0 ? all_dists.data() : NULL);
    MPI_Gather(&dist, 1, MPI_DOUBLE, recvbuf, 1, MPI_DOUBLE, 0, MPI_COMM_WORLD);

    if (rank == 0)
    {
        double best = std::numeric_limits<double>::infinity();
        for (int i = 0; i < nprocs; ++i)
        {
            std::cout << "Rank " << i << " distance = " << all_dists[i] << "\n";
            if (all_dists[i] < best)
                best = all_dists[i];
        }
        std::cout << "Best distance = " << best << "\n";
    }

    MPI_Finalize();
    return 0;
}
