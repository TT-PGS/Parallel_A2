import unittest
from part3.algorithms import astar_parallel as astar_solver

class SimpleGraph:
    """
    A simple adjacency-based graph for unit testing.
    The graph is provided as a dictionary mapping nodes to a list of (neighbor, cost).
    """
    def __init__(self, edges):
        self._adj = edges

    def neighbors(self, u):
        return [v for v, _ in self._adj.get(u, [])]

    def __getitem__(self, u):
        return {v: [{'length': cost}] for v, cost in self._adj.get(u, [])}


def zero_h(_, __, ___):
    """
    Zero heuristic function (i.e., Dijkstra's behavior).
    """
    return 0


class TestHopPreference(unittest.TestCase):
    """
    Unit tests for A* with hop-aware tie-breaking. These tests verify that
    among paths with equal cost, the algorithm prefers the one with fewer direction changes.
    """

    def test_0001_with_circumstances(self):
        """
        A->B->C->D (3 steps, fewer hops) vs A->E->F->D (3 steps).
        Ensure that A->B->C->D is chosen due to fewer direction changes.
        """
        g = SimpleGraph({
            'A': [('B',1), ('E',1)],
            'B': [('C',1)],
            'C': [('D',1)],
            'E': [('F',1)],
            'F': [('D',1)],
            'D': []
        })
        path, fvec = astar_solver('A', 'D', g, zero_h, None, "FineGrain", 4)
        self.assertEqual(path, ['A', 'B', 'C', 'D'])
        self.assertEqual(fvec[0], 3)

    def test_0002_with_circumstances(self):
        """
        Path A->X->D vs A->B->C->D (same cost).
        Ensure that A->X->D is preferred due to fewer hops.
        """
        g = SimpleGraph({
            'A': [('X',1), ('B',1)],
            'X': [('D',2)],
            'B': [('C',1)],
            'C': [('D',1)],
            'D': []
        })
        path, fvec = astar_solver('A', 'D', g, zero_h, None, "FineGrain", 4)
        self.assertEqual(path, ['A', 'X', 'D'])
        self.assertEqual(fvec[0], 3)

    def test_0003_with_circumstances(self):
        """
        A->B->C->D vs A->P->Q->R->D.
        Ensure that shorter path A->B->C->D is chosen.
        """
        g = SimpleGraph({
            'A': [('B',1), ('P',1)],
            'B': [('C',1)],
            'C': [('D',1)],
            'P': [('Q',1)],
            'Q': [('R',1)],
            'R': [('D',1)],
            'D': []
        })
        path, fvec = astar_solver('A', 'D', g, zero_h, None, "FineGrain", 4)
        self.assertEqual(path, ['A', 'B', 'C', 'D'])
        self.assertEqual(fvec[0], 3)


if __name__ == "__main__":
    print("Running hop-preference unit tests...")
    unittest.main(verbosity=2)
