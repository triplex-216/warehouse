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
    print_matrix(init_mat)
    init_mat = reduce_matrix(init_mat, multi_access=True)
    print_matrix(init_mat)
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

        # Process item nodes
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


def reduce_matrix(mat: np.ndarray, multi_access=False):
    if multi_access:

        def compress_minimum_matrix(mat: np.ndarray):
            compressed_mat_size = int(mat_size / 4)
            compressed_mat = np.full(
                shape=(compressed_mat_size, compressed_mat_size),
                fill_value=float("inf"),
            )
            for r in range(compressed_mat_size):
                for c in range(compressed_mat_size):
                    # For each 4x4 block, get local minimum
                    block = mat[r * 4 : (r + 1) * 4, c * 4 : (c + 1) * 4]
                    compressed_mat[r][c] = block.min()
            return compressed_mat

        mat_size = mat.shape[0]

        # Reduce by row
        compressed_mat = compress_minimum_matrix(mat)
        print_matrix(compressed_mat)
        row_reduce_costs = [min(row) for row in compressed_mat]
        for r, cost in enumerate(row_reduce_costs):
            print(f"Reducing rows {r*4} ~ {(r+1)*4} by {cost}")
            # print(mat[r * 4 : (r + 1) * 4])
            mat[r * 4 : (r + 1) * 4] -= cost
            # print(mat[r * 4 : (r + 1) * 4])
            print(cost)
        print_matrix(mat)

        # Reduce by col
        compressed_mat = compress_minimum_matrix(mat)
        print_matrix(compressed_mat)
        col_reduce_costs = [min(col) for col in compressed_mat.T]
        for c, cost in enumerate(col_reduce_costs):
            print(f"Reducing cols {c*4} ~ {(c+1)*4} by {cost}")
            # print(mat[:, c * 4 : (c + 1) * 4])
            mat[:, c * 4 : (c + 1) * 4] -= cost
            # print(mat[:, c * 4 : (c + 1) * 4])
            print(cost)
        print_matrix(mat)

        print_matrix(compress_minimum_matrix(mat))
        return mat


def print_matrix(mat):
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
