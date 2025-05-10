```
project_root/
├── part1/                               # Serial A* implementation
│   ├── README.md
│   ├── __init__.py
│   ├── unittest.py
│   ├── unittest_under_circumstances.py
│   ├── benchmark.py
│   └── algorithms.py                    # astar_solver with dynamic h(x) and f-vector

```

commands:
python -m unittest -v .\part1\unittest.py                           # to run unittest
python -m unittest -v .\part1\unittest_under_circumstances.py       # to run unittest under circumstances
python -m unittest -v .\part1\benchmark.py                          # to run benchmark and get results with real maps
