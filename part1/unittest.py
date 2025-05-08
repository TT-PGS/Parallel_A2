import unittest
from collections import deque
from part1.algorithms import astar_solver  # adjust to your actual package

class SimpleGraph:
    def __init__(self, edges):
        # edges: dict node -> list of (neighbor, cost)
        self._adj = edges

    def neighbors(self, u):
        return [v for v, _ in self._adj.get(u, [])]

    def __getitem__(self, u):
        return { v: [ {'length': cost} ] 
                 for v, cost in self._adj.get(u, []) }

def zero_h(u, v, _): 
    return 0

def exact_h(u, v, graph):
    dq = deque([(u, 0)])
    seen = {u}
    while dq:
        cur, d = dq.popleft()
        if cur == v:
            return d
        for nbr, cost in graph._adj.get(cur, []):
            if nbr not in seen:
                seen.add(nbr)
                dq.append((nbr, d + cost))
    return float('inf')

def manhattan_h(u, v, graph):
    # assume nodes are (x,y) tuples
    ux, uy = u; vx, vy = v
    return abs(ux - vx) + abs(uy - vy)


def fv(g, h):
    return ()  # no extras


# Test cases

class TestAStar(unittest.TestCase):
    def test_0001(self):
        """Straight line A→B→C, cost=2"""
        g = SimpleGraph({'A':[('B',1)], 'B':[('C',1)], 'C':[]})
        path, fvec = astar_solver('A','C', g, exact_h, fv)
        self.assertEqual(path, ['A','B','C'])
        self.assertEqual(fvec[0], 2)

    def test_0002(self):
        """Zero‐cost edge A→B (0), B→C (1)"""
        g = SimpleGraph({'A':[('B',0)], 'B':[('C',1)], 'C':[]})
        path, fvec = astar_solver('A','C', g, zero_h, fv)
        self.assertEqual(path, ['A','B','C'])
        self.assertEqual(fvec[0], 1)

    def test_0003(self):
        """Single‐obstacle detour A→{B,C}→D, cost=2"""
        g = SimpleGraph({
            'A':[('B',1),('C',1)],
            'B':[('D',1)],
            'C':[('D',1)],
            'D':[]
        })
        path, fvec = astar_solver('A','D', g, zero_h, fv)
        self.assertIn(path, [['A','B','D'], ['A','C','D']])
        self.assertEqual(fvec[0], 2)

    def test_0004(self):
        """Tie‐breaking: two equal‐cost routes via B or C"""
        # same as test_04 but ensuring length==3
        g = SimpleGraph({
            'A':[('B',1),('C',1)],
            'B':[('D',1)],
            'C':[('D',1)],
            'D':[]
        })
        path, fvec = astar_solver('A','D', g, zero_h, fv)
        self.assertEqual(len(path), 3)
        self.assertEqual(fvec[0], 2)

    def test_0005(self):
        """No path available => (None,None)"""
        g = SimpleGraph({'A':[('B',1)], 'B':[], 'G':[]})
        path, fvec = astar_solver('A','G', g, zero_h, fv)
        self.assertIsNone(path)
        self.assertIsNone(fvec)

    def test_0006(self):
        """3x3 grid, obstacle row in middle, cost=4"""
        # coordinates as (x,y), 0≤x,y≤2
        edges = {}
        blocked = {(0,1), (1,1)}
        start, goal = (0,0), (2,2)
        for x in range(3):
            for y in range(3):
                u = (x,y)
                nbrs = []
                for dx,dy in [(1,0),(-1,0),(0,1),(0,-1)]:
                    v = (x+dx, y+dy)
                    if 0<=v[0]<3 and 0<=v[1]<3 and v not in blocked:
                        nbrs.append((v,1))
                edges[u] = nbrs
        g = SimpleGraph(edges)
        path, fvec = astar_solver(start, goal, g, manhattan_h, fv)
        self.assertEqual(path, [(0,0),(1,0),(2,0),(2,1),(2,2)])
        self.assertEqual(fvec[0], 4)
        # ensure a valid path around the obstacle
        self.assertTrue(path[0]==start and path[-1]==goal)
        self.assertEqual(len(path)-1, 4)

    def test_0007(self):
        """Graph with cycle A→B→C→A and C→D"""
        g = SimpleGraph({
            'A':[('B',1)],
            'B':[('C',1)],
            'C':[('A',1),('D',1)],
            'D':[]
        })
        path, fvec = astar_solver('A','D', g, zero_h, fv)
        self.assertEqual(path, ['A','B','C','D'])
        self.assertEqual(fvec[0], 3)

    def test_0008(self):
        """Heuristic consistency on chain A–B–C"""
        g = SimpleGraph({'A':[('B',1)], 'B':[('C',1)], 'C':[]})
        for u, nbrs in g._adj.items():
            for v, cost in nbrs:
                self.assertLessEqual(
                    exact_h(u,'C',g),
                    cost + exact_h(v,'C',g)
                )
    def test_0009(self):
        """4×4 grid with a full obstacle wall at x=1 except a gap at (1,2)."""
        # build grid and block x=1 for all y except y=2
        edges = {}
        blocked = {(1,0), (1,1), (1,3)}
        for x in range(4):
            for y in range(4):
                u = (x,y)
                nbrs = []
                if u not in blocked:
                    for dx, dy in [(1,0),(-1,0),(0,1),(0,-1)]:
                        v = (x+dx, y+dy)
                        if 0 <= v[0] < 4 and 0 <= v[1] < 4 and v not in blocked:
                            nbrs.append((v,1))
                edges[u] = nbrs
        g = SimpleGraph(edges)
        start, goal = (0,0), (3,3)
        path, fvec = astar_solver(start, goal, g, manhattan_h, fv)
        # must detour through the single gap at (1,2):
        # [(0, 0), (0, 1), (0, 2), (1, 2), (2, 2), (2, 3), (3, 3)], cost = 6
        self.assertEqual(fvec[0], 6)
        self.assertIn((1,2), path)

    def test_0010(self):
        """10×10 grid with a full obstacle wall at x=5, x = 7 except a gap at (5,5), (7,3) ."""
        # build grid and block x=5 for all y except y=5
        edges = {}
        blocked = {(5, y) for y in range(10) if y != 5} | {(7, y) for y in range(10) if y != 3}
        for x in range(10):
            for y in range(10):
                u = (x, y)
                nbrs = []
                if u not in blocked:
                    for dx, dy in [(1,0), (-1,0), (0,1), (0,-1)]:
                        v = (x + dx, y + dy)
                        if 0 <= v[0] < 10 and 0 <= v[1] < 10 and v not in blocked:
                            nbrs.append((v, 1))
                edges[u] = nbrs

        g = SimpleGraph(edges)
        start, goal = (0, 0), (9, 9)
        path, fvec = astar_solver(start, goal, g, manhattan_h, fv)
        self.assertEqual(fvec[0], 22)
        self.assertEqual(len(path) - 1, 22)
        self.assertIn((5, 5), path)
        self.assertIn((7, 3), path)
        self.assertEqual(path[0], start)
        self.assertEqual(path[-1], goal)

# —————————————————————————————


# —————————————————————————————
if __name__ == "__main__":
    print("Running unit tests without dynamic characteristics...")
    suite = unittest.TestLoader().loadTestsFromTestCase(TestAStar)
    unittest.TextTestRunner(verbosity=2).run(suite)
    print("All tests completed.")