import resource
import time
from lib.core import *
from lib.route import *
from lib.tui import *
from lib.genetic import *
from lib.bnb import *
from itertools import combinations, product
from random import sample

DATASET = "data/qvBox-warehouse-data-s23-v01.txt"
map_data, prod_db = read_inventory_data(DATASET)
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

# order_list = [prod_db[item] for item in test_order_lists[2]]
ids = [736830, 208660, 10438, 633, 68048, 105912, 5329]
ids = sample(test_order_lists[4], k=7)
print(ids)
order_list = [prod_db[item] for item in ids]
# order_list = [prod_db[item] for item in [108335, 391825, 340367]]
# order_list = [prod_db[item] for item in [108335, 391825]]

item_locations = get_item_locations(prod_db, [p.id for p in order_list])
item_nodes = [prod_to_node(prod) for prod in order_list]
start_node = SingleNode(coord=(0, 0), map=map_data)
# end_node = SingleNode(coord=(0, 0), map=map_data)
# end_node = SingleNode(coord=(20, 11), map=map_data)
end_node = SingleNode(coord=(20, 20), map=map_data)
# all_nodes = [start_node] + item_nodes
all_nodes = [start_node] + item_nodes + [end_node]
generate_cost_graph(all_nodes, start_node=start_node, end_node=end_node)
start = time.time()
bnb_instr, bnb_total_cost, bnb_route = find_route(
        item_nodes=item_nodes,
        start_node=start_node,
        end_node=end_node,
        algorithm='b',
)
# print(f"Cost={len(_route)}, Path={[ap.coord for ap in path]}")
# print(instructions)
print(f"BnB use {time.time() - start} seconds")

peak_mem_in_kb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
peak_mem_str = f"{peak_mem_in_kb} KiB ({(peak_mem_in_kb/1024):0.2f} MiB)"
print(peak_mem_str)


# # Draw text map
# map_text = draw_text_map(map_data)
# # Add route paths to map
# map_text = add_paths_to_map(map_text, bnb_route, item_locations)
# # Add axes to map for easier reading
# map_full = add_axes_to_map(map_text, rows, cols)

# warn("\nWAREHOUSE MAP\n")
# print_map(map_full)
# print(bnb_instr)

# NN
nn_instr, nn_total_cost, nn_route = find_route(
        item_nodes=item_nodes,
        start_node=start_node,
        end_node=end_node,
        algorithm='n',
)
# # Draw text map
# map_text = draw_text_map(map_data)
# # Add route paths to map
# map_text = add_paths_to_map(map_text, nn_route, item_locations)
# # Add axes to map for easier reading
# map_full = add_axes_to_map(map_text, rows, cols)
# print_map(map_full)
# print(nn_instr)
print(f"Total distance is {len(bnb_route)} using BnB algorithm.")
print(f"Total distance is {len(nn_route)} using Nearest-Neighbor algorithm.")

pass
