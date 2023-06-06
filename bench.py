import resource
import timeit
from math import floor
from lib.core import read_inventory_data
from lib.route import *
from random import sample

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
    [
        633,
        1321,
        3401,
        5329,
        10438,
        372539,
        396879,
        16880,
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
        20373,
    ],
]
DEFAULT_REPS = (
    5  # Default repetitions to test each algorithm and calculate an average time
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

    nn_times = []
    bab_times = []
    test_cases_truncated = []
    for idx, case in enumerate(TEST_CASES):
        test_cases_truncated.append(sample(case, idx + 1))
    for idx, order in enumerate(test_cases_truncated):
        # if len(order) >= 5:
        #     order = sample(order, k=5)  # limit to 5 inputs for bnb's sake

        items = get_item(prod_db, order)
        item_nodes = [prod_to_node(prod) for prod in items]
        start_node = SingleNode(coord=(0, 0), map=warehouse_map)
        end_node = SingleNode(coord=(0, 0), map=warehouse_map)

        print(f"Testing nearest neighbor with input {order}...")
        nn_times.append(
            get_avg_runtime(
                lambda: find_route_with_timeout(
                    item_nodes, start_node, end_node, "n", 5
                )
            )
        )
        print(f"Testing BnB with input {order}...")
        bab_times.append(
            get_avg_runtime(
                lambda: find_route_with_timeout(
                    item_nodes, start_node, end_node, "b", 5
                )
            )
        )

    m = get_peak_mem()

    # report phase
    print("\nTest Report: \n============\n")
    print(f"Average execution time of branch and bound: ")
    for idx, t in enumerate(bab_times):
        print(f"Size={len(test_cases_truncated[idx])}: {t:.6f} seconds ({test_cases_truncated[idx]})")
    print(f"Average execution time of greedy: ")
    for idx, t in enumerate(nn_times):
        print(f"Size={len(test_cases_truncated[idx])}: {t:.6f} seconds ({test_cases_truncated[idx]})")

    print("\nComparison: ")
    print("Size\t|B&B\t|Greedy")  # Header
    for idx, t in enumerate(zip(bab_times, nn_times)):
        print(f"{len(test_cases_truncated[idx])}\t|{t[0]:.3f}s\t|{t[1]:.3f}s")

    print(f"Peak memory usage: {m}")
