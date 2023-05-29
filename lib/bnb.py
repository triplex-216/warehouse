import numpy as np
from .route import Node, AccessPoint
from random import choice

"""
Branch and bound algorithm
"""


def branch_and_bound(nodes: list[Node], start: Node, end: Node):
    # 1. Process nodes and access points information
    all_nodes = [start] + nodes + [end]  # S(tart), A, B, ..., E(nd)
    # all_nodes_coordinates = [n.coord for n in all_nodes]
    # 2. Setup the initial matrix and reduce
    init_mat = setup_matrix(nodes=all_nodes, multi_access=False)
    init_mat = reduce_matrix(init_mat)
    # 3. Start branching

    # Randomly pick a node to begin with

    pass


def setup_matrix(nodes: list[Node], multi_access=False):
    if multi_access:
        raise Exception("Multi access unsupported")

    # Initialize matrix and fill with infinite
    mat_size = len(nodes)
    mat = np.full(shape=(mat_size, mat_size), fill_value=float("inf"))

    for idx, n in enumerate(nodes):
        node_idx_range = range(idx * 4, idx * 4 + 4)
        

    return mat


def reduce_matrix(mat):
    return mat
