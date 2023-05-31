import numpy as np
from .route import Node, SingleNode, AccessPoint
from random import choice
from math import floor

"""
Branch and bound algorithm
"""


def branch_and_bound(
    nodes: list[Node | SingleNode], start: Node | SingleNode, end: Node | SingleNode
):
    # 1. Process nodes and access points information
    all_nodes = [start] + nodes + [end]  # S(tart), A, B, ..., E(nd)
    # all_nodes_coordinates = [n.coord for n in all_nodes]
    # 2. Setup the initial matrix and reduce
    init_mat = setup_matrix(nodes=all_nodes, multi_access=True)
    print_matrix(init_mat, all_nodes)
    init_mat = reduce_matrix(init_mat, multi_access=True)
    # 3. Start branching

    # Randomly pick a node to begin with

    pass


def setup_matrix(nodes: list[Node | SingleNode], multi_access=False):
    start_node = nodes[0]
    end_node = nodes[-1]

    if multi_access:
        # Multi Access
        # Initialize matrix and fill with infinite
        mat_size = len(nodes * 4)
        mat = np.full(shape=(mat_size, mat_size), fill_value=float("inf"))

        # Firstly, process the item nodes' rows/cols
        for node in nodes:
            node_idx = nodes.index(node)
            rows_range = range(node_idx * 4, node_idx * 4 + 4)
            for r in rows_range:
                curr_ap = node.neighbors_as_list[r % 4]
                if curr_ap:  # Continue if current AP exists
                    for c in range(r, mat_size):
                        dest_node = nodes[floor(c / 4)]
                        dest_ap = dest_node.neighbors_as_list[c % 4]

                        if (
                            node is not dest_node and dest_ap
                        ):  # Set grid to cost if destination AP exists
                            mat[r][c] = curr_ap.dv[dest_ap][0]
                            print(f"({r},{c}) <== {mat[r][c]} ({dest_node.coord})")

        # Process start/end nodes
        start_node_range = range(0, 4)
        end_node_range = range(mat_size - 4, mat_size)

        for r in start_node_range:
            for c in end_node_range:
                mat[r, c] = 0  # Start => End must be 0

        for r in end_node_range:
            for c in start_node_range:
                mat[r, c] = float("inf")  # End => Start must be infinity

        # Copy the upper half to the lower half
        row_indices, col_indices = np.triu_indices(mat_size, k=1)
        for r, c in zip(row_indices, col_indices):
            mat[c, r] = mat[r, c]

        return mat

    else:
        # Single Access
        # Initialize matrix and fill with infinite
        mat_size = len(nodes)
        mat = np.full(shape=(mat_size, mat_size), fill_value=float("inf"))

        for node_idx, node in enumerate(nodes):
            rows_range = range(node_idx * 4, node_idx * 4 + 4)

        return mat


def reduce_matrix(mat, multi_access=False):
    return mat


def print_matrix(mat, nodes: list[Node]):
    header = " " * 3
    lines = []
    for idx, row in enumerate(mat):
        offset = idx % 4
        match offset:
            case 0:
                dir = "N"
            case 1:
                dir = "E"
            case 2:
                dir = "S"
            case 3:
                dir = "W"
            case _:
                dir = "?"

        node_name = f"{floor(idx / 4)}{dir}"
        line = f"{node_name} "
        for num in row:
            line += f"{num:<4.0f} " if num != float("inf") else "---- "

        header += f"{node_name:5}"
        lines.append(line)

    print(header)
    [print(line) for line in lines]
