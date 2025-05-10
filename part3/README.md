```
├── part3/                               # Merged parallel A*from part1 and part2
│   ├── __init__.py
│   ├── unittest_for_fine_grain.py
│   ├── unittest_under_circumstances_for_fine_grain.py
│   ├── unittest_for_optimictis.py
│   ├── unittest_under_circumstances_for_optimictis.py
│   ├── benchmark.py
│   └── algorithms_parallel.py           # integrated parallel A* implementation
```

commands:
python -m unittest -v .\part3\unittest_for_fine_grain.py                            # to run unittest with fine-grain version
python -m unittest -v .\part3\unittest_under_circumstances_for_fine_grain.py        # to run unittest under circumstances with fine-grain version

python -m unittest -v .\part3\unittest_for_optimictis.py                            # to run unittest with optimictis version
python -m unittest -v .\part3\unittest_under_circumstances_for_optimictis.py        # to run unittest under circumstances with optimictis version

python -m unittest -v .\part3\benchmark.py                                          # to run benchmark and get results with real maps
