import resource
import timeit
from math import floor
from lib.core import read_inventory_data
from lib.route import *

TEST_CASES = [
    [108335],
    [108335, 391825, 340367, 286457, 661741],
    [281610, 342706, 111873, 198029, 366109, 287261, 76283, 254489, 258540, 286457],
    [
        427230,
        372539,
        396879,
        391680,
        208660,
        105912,
        332555,
        227534,
        68048,
        188856,
        736830,
        736831,
        479020,
        103313,
        1,
    ],
    # [
    #     633,
    #     1321,
    #     3401,
    #     5329,
    #     10438,
    #     372539,
    #     396879,
    #     16880,
    #     208660,
    #     105912,
    #     332555,
    #     227534,
    #     68048,
    #     188856,
    #     736830,
    #     736831,
    #     479020,
    #     103313,
    #     1,
    #     20373,
    # ],
]
DEFAULT_REPS = (
    1  # Default repetitions to test each algorithm and calculate an average time
)


def get_avg_runtime(func, reps=DEFAULT_REPS):
    execution_time = timeit.timeit(func, number=reps) / reps
    return execution_time


def get_peak_mem():
    peak_mem_in_kb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    peak_mem_str = f"{peak_mem_in_kb} KiB ({(peak_mem_in_kb/1024):0.2f} MiB)"
    return peak_mem_str


if __name__ == "__main__":
    # startup phase
    warehouse_map, prod_db = read_inventory_data(
        "data/qvBox-warehouse-data-s23-v01.txt"
    )

    # testing phase

    greedy_times = []
    bab_times = []
    for idx, order in enumerate(TEST_CASES):
        print(f"Testing greedy with input {order}...")
        greedy_times.append(
            get_avg_runtime(
                lambda: greedy(
                    map=warehouse_map, prod_db=prod_db, item_ids=order, start=(0, 0)
                ),
            )
        )
        print(f"Testing B&B with input {order}...")
        bab_times.append(
            get_avg_runtime(
                lambda: branch_and_bound(
                    map=warehouse_map, prod_db=prod_db, item_ids=order, start=(0, 0)
                ),
            )
        )

    m = get_peak_mem()

    # report phase
    print(f"Average execution time of branch and bound: ")
    for idx, t in enumerate(bab_times):
        print(f"Size={len(TEST_CASES[idx])}: {t:.6f} seconds ({TEST_CASES[idx]})")
    print(f"Average execution time of greedy: ")
    for idx, t in enumerate(greedy_times):
        print(f"Size={len(TEST_CASES[idx])}: {t:.6f} seconds ({TEST_CASES[idx]})")
    
    print(f"Peak memory usage: {m}")
