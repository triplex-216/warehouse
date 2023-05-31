import matplotlib.pyplot as plt
from lib.core import *
from lib.route import *
from lib.tui import *
from itertools import combinations, product

DATASET = "data/qvBox-warehouse-data-s23-v01.txt"
map_data, prod_db = read_inventory_data(DATASET)

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

order_list = [prod_db[item] for item in test_order_lists[1]]


item_nodes = [prod_to_node(prod) for prod in order_list]
start_node = SingleNode(coord=(0, 0), map=map_data)
end_node = SingleNode(coord=(39, 20), map=map_data)
# nodes_list = [start_node] + item_nodes + [end_node]


generate_cost_graph(item_nodes, start_node=start_node, end_node=end_node)

res = greedy(items=item_nodes, start=start_node, end=end_node)

pass
