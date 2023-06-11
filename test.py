import resource
import time
from lib.core import *
from lib.route import *
from lib.tui import *
from lib.genetic import *
from lib.bnb import *

DATASET = "data/qvBox-warehouse-data-s23-v01.txt"
conf = Config()
read_inventory_data(DATASET, conf)
prod_db, map_data = conf.prod_db, conf.map_data
cols, rows = len(map_data), len(map_data[0])
test_order_lists = [
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


def run_bnb():
    order = test_order_lists[-1][:10]
    print(len(order), order)
    item_nodes = prod_to_node(prod_db=prod_db, map_data=map_data, id_list=order)

    start_node = SingleNode(coord=(0, 0), map=map_data)
    end_node = SingleNode(coord=(20, 20), map=map_data)

    all_nodes = [start_node] + item_nodes + [end_node]

    generate_cost_graph(all_nodes, start_node, end_node)

    bnb_instr, bnb_total_cost, bnb_route, _ = find_route_with_timeout(
        item_nodes=item_nodes,
        start_node=start_node,
        end_node=end_node,
        algorithm="b",
        timeout=15,
    )
    nn_instr, nn_total_cost, nn_route, _ = find_route_with_timeout(
        item_nodes=item_nodes,
        start_node=start_node,
        end_node=end_node,
        algorithm="n",
        timeout=15,
    )

    print(f"Total distance is {len(bnb_route)} using BnB algorithm.")
    print(f"Total distance is {len(nn_route)} using Nearest-Neighbor algorithm.")


def read_order_file(file_path):
    orders = {}

    if os.path.exists(file_path):
        id = 1
        with open(file_path) as csvfile:
            reader = csv.reader(csvfile, delimiter="\t")
            for curr in reader:
                orders[id] = [int(num) for num in curr[0].split(",")]
                id += 1

    return orders


if __name__ == "__main__":
    orders = read_order_file("data/qvBox-warehouse-orders-list-part01.txt")

    failed_cases = []

    for order in orders.values():
        break
        size_limit = 6
        if len(order) >= size_limit:
            order = order[:size_limit]

        item_nodes = [prod_to_node(prod_db[item]) for item in order]

        start_node = SingleNode(coord=(0, 0), map=map_data)
        end_node = SingleNode(coord=(20, 20), map=map_data)

        all_nodes = [start_node] + item_nodes + [end_node]

        generate_cost_graph(all_nodes, start_node, end_node)

        bnb_instr, bnb_total_cost, bnb_route = find_route(
            item_nodes=item_nodes,
            start_node=start_node,
            end_node=end_node,
            algorithm="b",
        )

        nn_instr, nn_total_cost, nn_route = find_route(
            item_nodes=item_nodes,
            start_node=start_node,
            end_node=end_node,
            algorithm="n",
        )

        print(f"Total distance is {len(bnb_route)} using BnB algorithm.")
        print(f"Total distance is {len(nn_route)} using Nearest-Neighbor algorithm.")

        if len(bnb_route) > len(nn_route):
            print(f"BnB is inferior to NN in {order}! ")
            failed_cases.append(order)

    peak_mem_in_kb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    peak_mem_str = f"{peak_mem_in_kb} KiB ({(peak_mem_in_kb/1024):0.2f} MiB)"
    print(peak_mem_str)

    print(f"Failed Cases: {failed_cases}")

    run_bnb()
    # import cProfile

    # cProfile.run("run_bnb()")
