project_root/
├── benchmark.py                         # benchmark runner for all versions
├── common/
│   └── common.py                        # load_map, load_point_pairs, setup_logger, setup directories
├── part1/                               # Serial A*implementation
│   ├── README.md
│   ├── __init__.py
│   └── algorithms.py                    # astar_solver with dynamic h(x) and f-vector
├── part2
│   ├── README.md
│   ├── __init__.py
│   ├── fine_grained_lock.py                    # fine-grained locking structure
│   ├── optimistic_synchronization.py           # Optimistic structure
│   ├── fine_grained_lock_ver2.py               # Updated fine-grained locking structure
│   ├── optimistic_synchronization_ver2.py      # Updated Optimistic structure
│   └── tester.py                               # A test of correctness and performance for two tructures
├── part3/                               # Merged parallel A*from part1 and part2
│   ├── __init__.py
│   └── algorithms_parallel.py           # Integrated parallel A* implementation
└── setup/                               # storage for maps and point files
    ├── maps/                            # Pickle files of loaded maps (auto-created)
    └── points/                          # Files listing start/goal pairs by city

link youtube for result: <https://www.youtube.com/playlist?list=PL5zvNdc-uZp_ej9yrAJEx_thENq-75o9q>

run:

python benchmark.py

the results will be stored in results folder (which is created after running)
