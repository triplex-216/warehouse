import resource
import timeit
from math import floor
from lib.core import read_inventory_data
from lib.route import *
from lib.tui import show_result
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
    1  # Default repetitions to test each algorithm and calculate an average time
)


def get_avg_runtime(f_alg, reps=DEFAULT_REPS):
    t_start = time()

    for _ in range(reps):
        res = f_alg()
        triggered_time_out = res[-1]
        if triggered_time_out:
            failed = True
            print("One of the function evaluations failed. ")
            return float("inf")

    execution_time = time() - t_start
    return execution_time


def get_peak_mem():
    peak_mem_in_kb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    peak_mem_str = f"{peak_mem_in_kb} KiB ({(peak_mem_in_kb/1024):0.2f} MiB)"
    return peak_mem_str


if __name__ == "__main__":
    # startup phase
    conf = Config()

    read_inventory_data("data/qvBox-warehouse-data-s23-v01.txt", conf=conf)
    prod_db = conf.prod_db
    map_data = conf.map_data

    # testing phase

    nn_times = []
    bnb_times = []
    # test_cases = TEST_CASES[:3]

    # ids, test_cases = read_order_file("data/qvBox-warehouse-orders-list-part01.txt")
    # for idx, case in enumerate(TEST_CASES):
    #     test_cases.append(sample(case, idx + 1))
    test_cases = TEST_CASES
    for idx, order in enumerate(TEST_CASES):
        if len(order) >= 10:
            order = order[:10]  # limit inputs for bnb's sake

        item_nodes = prod_to_node(prod_db=prod_db, map_data=map_data, id_list=order)
        start_node = SingleNode(coord=(0, 0), map=map_data)
        end_node = SingleNode(coord=(0, 0), map=map_data)
        item_locations = [prod_db[id] for id in order]

        print(f"Testing nearest neighbor with input {order}...")
        instr, total_cost, route, timeout = find_route(item_nodes, start_node, end_node, "n", -1)
        show_result(map_data, conf, item_locations, instr, total_cost, route, timeout)
        nn_times.append(
            get_avg_runtime(
                lambda: find_route(item_nodes, start_node, end_node, "n", -1)
            )
        )
        print(f"Testing BnB with input {order}...")
        instr, total_cost, route, timeout = find_route(item_nodes, start_node, end_node, "b", -1)
        show_result(map_data, conf, item_locations, instr, total_cost, route, timeout)
        bnb_times.append(
            get_avg_runtime(
                lambda: find_route(item_nodes, start_node, end_node, "b", -1)
            )
        )

    m = get_peak_mem()

    # report phase
    print("\nTest Report: \n============\n")
    print(f"Average execution time of branch and bound: ")
    for idx, t in enumerate(bnb_times):
        print(f"Size={len(test_cases[idx])}: {t:.6f} seconds ({test_cases[idx]})")
    print(f"Average execution time of greedy: ")
    for idx, t in enumerate(nn_times):
        print(f"Size={len(test_cases[idx])}: {t:.6f} seconds ({test_cases[idx]})")

    print("\nComparison: ")
    print("Size\t|B&B\t|Greedy")  # Header
    for idx, t in enumerate(zip(bnb_times, nn_times)):
        print(f"{len(test_cases[idx])}\t|{t[0]:.3f}s\t|{t[1]:.3f}s")

    print(f"Peak memory usage: {m}")
