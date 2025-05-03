```
project_root/
├── benchmark.py                         # benchmark runner for all versions
├── common/
│   └── common.py                        # load_map, load_point_pairs, setup_logger, setup directories
├── part1/                               # Serial A* implementation
│   ├── README.md
│   ├── __init__.py
│   └── algorithms.py                    # astar_solver with dynamic h(x) and f-vector
├── part2/                               # Concurrent structures (locking sets)
│   ├── README.md
│   ├── __init__.py
│   ├── fine_grained_lock.py                    # fine-grained locking structure
│   ├── optimistic_synchronization.py           # optimistic locking structure
│   ├── fine_grained_lock_ver2.py               # updated fine-grained version
│   ├── optimistic_synchronization_ver2.py      # updated optimistic version
│   └── tester.py                               # correctness & performance tester
├── part3/                               # Merged parallel A* from part1 and part2
│   ├── __init__.py
│   └── algorithms_parallel.py           # integrated parallel A* implementation
├── results/                             # Output folder (auto-created)
│   └── part2/
│       └── test_log.txt                 # test results from tester.py
└── setup/                               # storage for maps and point files
    ├── maps/                            # pickle files of loaded maps (auto-created)
    └── points/                          # files listing start/goal pairs by city
```

Link YouTube for result: <https://www.youtube.com/playlist?list=PL5zvNdc-uZp_ej9yrAJEx_thENq-75o9q>

Run:

```bash
python benchmark.py
```

The results will be stored in `results` folder (which is created after running).
