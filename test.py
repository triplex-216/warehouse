import matplotlib.pyplot as plt
from lib.core import *
from lib.route import *
from lib.tui import *
from branch_bound import branch_and_bound

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


item_count = 5
id_list = [108335, 391825, 340367, 286457, 661741]

for id_list in test_order_lists[:2]:
    locations = [(0,0)]+get_item_locations(prod_db, id_list)
    distance, path = branch_and_bound(map_data, locations)
    distance, route = path_to_route(map_data, path)
    print(f"Total distance is {distance}.")
    print(get_instructions(route, prod_db, id_list))
    


