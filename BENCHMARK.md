# Benchmarks on test inputs
This document describes the setup and inputs used during tests, as well as the result of each test case. 

# Test Setup
## Hardware Setup
- CPU: Intel(R) Core(TM) i7-6700 CPU @ 3.40GHz
- RAM: 15.5GiB

## Software Setup
- Operating System: Arch Linux (Kernel 6.3.3)
- Python: 3.11.3

# Test Procedure
1. The script (`bench.py`) reads test cases. 
2. Initiate the algorithm. The computation time is recorded and measured with Python's `time` module. Peak memory usage is measured with the `memory_profiler` module, which requires manual installation. 

# Test Cases

1. Size 1: 108335
2. Size 5: 108335, 391825, 340367, 286457, 661741
3. Size 10: 281610, 342706, 111873, 198029, 366109, 287261, 76283, 254489, 258540, 286457
4. Size 15: 427230, 372539, 396879, 391680, 208660, 105912, 332555, 227534, 68048, 188856, 736830, 736831, 479020, 103313, 1
5. Size 20: 633, 1321, 3401, 5329, 10438, 372539, 396879, 16880, 208660, 105912, 332555, 227534, 68048, 188856, 736830, 736831, 479020, 103313, 1, 20373

# Test Results

```
Test Report: 
============
Average execution time of branch and bound: 
Size=1: 0.125366 seconds ([108335])
Size=5: 0.230150 seconds ([108335, 391825, 340367, 286457, 661741])
Size=10: 0.722240 seconds ([281610, 342706, 111873, 198029, 366109, 287261, 76283, 254489, 258540, 286457])
Size=15: inf seconds ([427230, 372539, 396879, 391680, 208660, 105912, 332555, 227534, 68048, 188856, 736830, 736831, 479020, 103313, 1])
Size=20: inf seconds ([633, 1321, 3401, 5329, 10438, 372539, 396879, 16880, 208660, 105912, 332555, 227534, 68048, 188856, 736830, 736831, 479020, 103313, 1, 20373])
Average execution time of greedy: 
Size=1: 0.124400 seconds ([108335])
Size=5: 0.232755 seconds ([108335, 391825, 340367, 286457, 661741])
Size=10: 0.122786 seconds ([281610, 342706, 111873, 198029, 366109, 287261, 76283, 254489, 258540, 286457])
Size=15: 0.226795 seconds ([427230, 372539, 396879, 391680, 208660, 105912, 332555, 227534, 68048, 188856, 736830, 736831, 479020, 103313, 1])
Size=20: 0.818278 seconds ([633, 1321, 3401, 5329, 10438, 372539, 396879, 16880, 208660, 105912, 332555, 227534, 68048, 188856, 736830, 736831, 479020, 103313, 1, 20373])

Comparison: 
Size    |B&B    |Greedy
1       |0.125s |0.124s
5       |0.230s |0.233s
10      |0.722s |0.123s
15      |inf    |0.227s
20      |inf    |0.818s
Peak memory usage: 40072 KiB (39.13 MiB)
```

Note: 

- Nearest Neighbor algorithm does not necessarily produce the optimal route, however it can easily meet the time constraint of the application. 
- Branch and Bound does not finish at input sizes of more than 10 due to excessive RAM usage. 

# Test Case Reference Graph
![Test Case #1](figures/Figure_1.png)
![Test Case #2](figures/Figure_2.png)
![Test Case #3](figures/Figure_3.png)
![Test Case #4](figures/Figure_4.png)
![Test Case #5](figures/Figure_5.png)