```
project_root/
├── part2/                               # Concurrent structures (locking sets)
│   ├── README.md
│   ├── __init__.py
│   ├── fine_grained_lock.py                    # fine-grained locking structure
│   ├── optimistic_synchronization.py           # optimistic locking structure
│   ├── fine_grained_lock_ver2.py               # updated fine-grained version
│   ├── optimistic_synchronization_ver2.py      # updated optimistic version
│   └── tester.py                               # correctness & performance tester
```

run this command to test correctness and performance for two concurrent structures (check results/part2/*log):

python ./tester.py
