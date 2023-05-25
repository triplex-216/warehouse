import matplotlib.pyplot as plt
from lib.core import read_inventory_data
from lib.route import get_distance, get_neighbors

warehouse_map, prod_db = read_inventory_data("data/qvBox-warehouse-data-s23-v01.txt")

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

test_order_graphs = []
for case in test_order_lists:
    d = dict()
    for item in case:
        d[item] = (prod_db[item].x, prod_db[item].y)
    test_order_graphs.append(d)


def manhattan_dist(a, b):
    return ((a[0] - b[0]), (a[1] - b[1]))


def plot_graph(nodes: dict):
    # Define the access point directions
    access_points = {"n": (0, 1), "s": (0, -1), "e": (1, 0), "w": (-1, 0)}
    ap_reverse = dict(
        (v, k) for k, v in access_points.items()
    )  # Map coordinate offsets to direction strings

    # Create a new figure and axis
    fig, ax = plt.subplots()

    # Draw the nodes and their labels
    for node, (x, y) in nodes.items():
        ax.scatter(x, y, color="lightblue", s=500)
        ax.annotate(
            node,
            (x, y),
            textcoords="offset points",
            xytext=(0, 0),
            ha="center",
            va="center",
        )

        # Draw the access points as smaller nodes and display the texts beside them
        for ap_direction, (dx, dy) in access_points.items():
            ap_x = x + dx
            ap_y = y + dy
            ap_text = f"{node}-{ap_direction}"
            ax.scatter(ap_x, ap_y, color="white", edgecolor="black", s=300)
            ax.annotate(
                ap_text,
                (ap_x, ap_y),
                textcoords="offset points",
                xytext=(0, 0),
                ha="center",
                va="center",
                fontsize=8,
            )

            # Calculate and display distances between each node's access point to every other node's access point
            distances_text = f"{node}-{ap_direction}: \n"
            distances_to_aps = dict()
            for other_node, (other_x, other_y) in nodes.items():
                if node != other_node:
                    src_neighbors, dest_neighbors = get_neighbors(
                        warehouse_map, nodes[node]
                    ), get_neighbors(warehouse_map, nodes[other_node])

                    distances = get_distance(
                        warehouse_map, nodes[node], nodes[other_node]
                    )

                    for (src, dest), cost in distances.items():
                        if src in src_neighbors and dest in dest_neighbors:
                            distances_to_aps[
                                f"{other_node}-{ap_reverse[manhattan_dist(dest,nodes[other_node])]}"
                            ] = cost
            for dest, cost in distances_to_aps.items():
                distances_text += f"{dest}: {cost}\n"

            ax.annotate(
                distances_text,
                (ap_x, ap_y),
                textcoords="offset points",
                # xytext=(20, 0),
                # ha="center",
                # va="center",
                fontsize=6,
                bbox=dict(boxstyle="round", fc="w", ec="gray", alpha=0.9),
            )

    # Set axis limits and labels
    # ax.set_xlim(0, 12)
    # ax.set_ylim(0, 8)
    # ax.set_xticks([])
    # ax.set_yticks([])

    # Set the title and display the graph
    ax.set_title("Warehouse Graph")
    plt.show()


if __name__ == "__main__":
    # plot_graph(test_order_graphs[1])
    for g in test_order_graphs:
        plot_graph(g)
