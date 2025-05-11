```
project_root/
├── part2/                               # Concurrent structures (locking sets)
│   ├── README.md
│   ├── __init__.py
│   ├── fine_grained_lock.py                    # fine-grained locking structure
│   ├── optimistic_synchronization.py           # optimistic locking structure
│   ├── unittest_finegrainedset.py              # unittest for fine-grained version
│   ├── unittest_for_optimictis.py              # unittest for optimistic version
│   └── unittest_for_performance.py             # performance tester
```

commands:

python -m unittest -v .\part2\unittest_finegrainedset.py        # to run unittest with fine-grain structure

python -m unittest -v .\part2\unittest_for_optimictis.py        # to run unittest which optimictis structure

python -m unittest -v .\part2\unittest_for_performance.py       # to run performance test for fine-grain and optimictis structures
