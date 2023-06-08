from lib.core import *
from lib.route import *
from lib.tui import *
from gt import *


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


def prod_to_node(order_list):
    coord_set = set()
    item_nodes = []
    for prod in order_list:
        if (prod.x, prod.y) in coord_set:
            continue
        else:
            item_nodes.append(Node(prod.id, (prod.x, prod.y), prod._map))
            coord_set.add((prod.x, prod.y))
    return item_nodes



if __name__ == "__main__":
    order_list = [prod_db[item] for item in test_order_lists[1]]
    item_nodes = prod_to_node(order_list)
    
    start_node = SingleNode(coord=(0, 0), map=map_data)
    end_node = SingleNode(coord=(39, 20), map=map_data)

    input_nodes = [start_node] + item_nodes + [end_node]
    generate_cost_graph(input_nodes, start_node, end_node)

    # at least 30 rounds
    rounds = max(int((len(input_nodes) ** 2) / 2), 30)
    
    population, fit = genetic(item_nodes, start_node, end_node, rounds)
    print([n.coord for n in population], fit)
