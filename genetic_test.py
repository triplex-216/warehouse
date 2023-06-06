import matplotlib.pyplot as plt
from lib.core import *
from lib.route import *
from lib.tui import *
from lib.genetic import *
from itertools import combinations, product
from random import sample

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


def prod_to_node(prod: Prod):
    return Node(prod.id, (prod.x, prod.y), prod._map)


def generate_cost_graph(
    item_nodes: list[Node], start_node: Node = None, end_node: Node = None
) -> None:
    """
    Generate all edges between all possible Access Point pairs between
    all pairs of nodes from nodes_list
    There is no return, since the edges are stored in APs' Distance Vectors

    start_node and end_node can be absent
    """
    if start_node:
        item_nodes.insert(0, start_node)
    if end_node:
        item_nodes.append(end_node)

    edges = 0
    for a, b in combinations(item_nodes, 2):
        ap_1: AccessPoint  # Type hints for IDE
        ap_2: AccessPoint
        for ap_1, ap_2 in product(a.neighbors.values(), b.neighbors.values()):
            # Skip if the AP pair has been calculated
            if ap_2 in ap_1.dv.keys():
                continue

            dist, route = cost(a._map, ap_1.coord, ap_2.coord)
            ap_1.add_path(destination=ap_2, distance=dist, path=route)
            edges += 1
            # print(f"{ap_1.coord} -> {ap_2.coord}: {dist}")


def draw_graph(nodes: list[SingleNode]):
    # Create a figure and axes
    fig, ax = plt.subplots()

    for n in nodes:
        x, y = n.coord
        ax.plot(x, y, "o", color="red", markersize=10)
        ax.text(x + 0.1, y + 0.1, f"({x},{y})", fontsize=10)

        single_ap = next(iter((n.neighbors.values())))
        for dest, (dist, _route) in single_ap.dv.items():
            x_coords = (n.coord[0], dest.parent.coord[0])
            y_coords = (n.coord[1], dest.parent.coord[1])

            x_center, y_center = sum(x_coords) / 2, sum(y_coords) / 2
            ax.plot(x_coords, y_coords, "k-")
            ax.text(
                x_center + 0.5,
                y_center + 0.5,
                str(dist),
                fontsize=10,
                ha="center",
                va="center",
            )

    ax.set_aspect("equal")

    # Display the graph
    plt.show()


if __name__ == "__main__":
    order_list = [prod_db[item] for item in test_order_lists[1]]
    item_nodes = [prod_to_node(prod) for prod in order_list]
    start_node = SingleNode(coord=(0, 0), map=map_data)
    end_node = SingleNode(coord=(39, 20), map=map_data)

    single_access_nodes = [
        SingleNode(coord=(p.x, p.y), map=map_data, access_self=False)
        for p in order_list[:3]
    ]
    worker_node = start_node
    input_nodes = [start_node] + single_access_nodes
    generate_cost_graph(input_nodes)

    population, fit = genetic(input_nodes)
    # print([n.coord for n in population[0]], 1 / fit[0])

    draw_graph(input_nodes)
