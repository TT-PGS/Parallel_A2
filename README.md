project_root/
├── benchmark.py             # benchmark runner for all versions
├── common/
│   └── common.py            # load_map, load_point_pairs, setup_logger, setup directories
├── part1/                   # Serial A*implementation
│   ├── __init__.py
│   └── algorithms.py        # astar_serial with dynamic h(x) and f-vector
├── part2/                   # Concurrent A* variants
│   ├── __init__.py
│   ├── algorithms_finegrain.py  # A*with fine-grained locking
│   └── algorithms_variant.py    # Alternative concurrent A* variant
├── part3/                   # Merged parallel A*from part1 and part2
│   ├── __init__.py
│   └── algorithms_parallel.py    # Integrated parallel A* implementation
└── setup/                   # storage for maps and point files
    ├── maps/                # Pickle files of loaded maps (auto-created)
    └── points/              # Files listing start/goal pairs by city

link youtube for result: <https://www.youtube.com/playlist?list=PL5zvNdc-uZp_ej9yrAJEx_thENq-75o9q>

run:

python benchmark.py

the results will be stored in results folder (which is created after running    )
