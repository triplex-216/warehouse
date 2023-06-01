from __future__ import annotations
import numpy as np
from .route import Node, SingleNode, AccessPoint
from random import choice
from math import floor
from copy import deepcopy, copy

import heapq


class PriorityQueue:
    """
    An implementation of Priority Queue with heapq
    Generated with ChatGPT
    """

    def __init__(self):
        self._queue = []
        self._index = 0

    def is_empty(self):
        return len(self._queue) == 0

    def enqueue(self, item, priority):
        heapq.heappush(self._queue, (priority, self._index, item))
        self._index += 1

    def dequeue(self):
        if self.is_empty():
            raise IndexError("Priority queue is empty")
        _, _, item = heapq.heappop(self._queue)
        return item


class TreeNode:
    def __init__(
        self,
        cost: int,
        path: list[AccessPoint],
        matrix: np.ndarray,
        parent_tree_node: TreeNode = None,
    ) -> None:
        self.cost = cost
        self.path = path
        self.matrix = matrix
        self.parent_node = parent_tree_node

    @property
    def visited_nodes(self):
        return set([ap.parent for ap in self.path])


"""
Branch and bound algorithm
"""


def branch_and_bound(
    item_nodes: list[Node | SingleNode],
    start_node: Node | SingleNode,
    # end_node: Node | SingleNode,
):
    def mark_as_visited(mat: np.ndarray, src_ap_idx: int, dest_ap_idx: int):
        """
        "Visit" an AP by marking the source AP's row and the destination AP's
        column as infinity.
        """
        src_node_idx = floor(src_ap_idx / 4)
        dest_node_idx = floor(dest_ap_idx / 4)

        mat[src_node_idx * 4 : (src_node_idx + 1) * 4] = float("inf")
        mat[:, dest_node_idx * 4 : (dest_node_idx + 1) * 4] = float("inf")

        for r in range(dest_node_idx * 4, (dest_node_idx + 1) * 4):
            if r != dest_ap_idx:
                mat[r] = float("inf")

        return mat

    def calc_path_cost(path: list[AccessPoint], start_ap: AccessPoint):
        start_index = path.index(start_ap)
        path_corrected = path[start_index:] + path[:start_index]

        cost = 0
        for idx in range(len(path_corrected) - 1):
            curr, next = path_corrected[idx], path_corrected[idx + 1]
            cost += curr.dv[next][0]

        return cost

    # 1. Process nodes and access points information
    all_nodes = [start_node] + item_nodes   # S(tart), A, B, ..., E(nd)
    # all_nodes = [start_node] + item_nodes + [end_node]  # S(tart), A, B, ..., E(nd)
    # 2. Setup the initial matrix and reduce
    init_mat, dict_ap_to_idx = setup_matrix(nodes=all_nodes)
    # print_matrix(init_mat)
    init_mat, init_reduced_cost = reduce_matrix(init_mat)
    # print_matrix(init_mat)

    # 3. Start branching

    # Randomly pick a node
    # init_node = start_node
    init_node = choice(all_nodes)
    # if init_node is start_node:
    #     init_node = end_node

    print(f"Initializing BnB @ {init_node.coord}")
    init_aps = init_node.aps

    # path = []
    pq = PriorityQueue()

    for ap in init_aps:
        # Set init node column to infinity (can't be visited from
        # any node, since it's the first in path)
        mat_copy = init_mat.copy()
        node_col_idx = all_nodes.index(init_node)
        mat_copy[:, node_col_idx * 4 : (node_col_idx + 1) * 4] = float("inf")
        
        for r in range(node_col_idx * 4, (node_col_idx + 1) * 4):
            if r != dict_ap_to_idx[ap]:
                mat_copy[r] = float("inf")

        pq.enqueue(
            TreeNode(
                cost=init_reduced_cost,
                path=[ap],
                matrix=mat_copy,
                parent_tree_node=None,
            ),
            priority=init_reduced_cost,
        )
        # print(f"Enqueued {[ap.coord]}")

    best_tree_node = None

    while pq:
        current_tree_node: TreeNode
        current_tree_node = pq.dequeue()
        current_ap = current_tree_node.path[-1]

        current_path = current_tree_node.path
        current_mat = current_tree_node.matrix

        # Check if all nodes have been visited
        if len(current_tree_node.path) == len(all_nodes):
            best_tree_node = current_tree_node
            print(calc_path_cost(best_tree_node.path, start_node.aps[0]))
            return best_tree_node.cost, best_tree_node.path

        for next_ap, _ in current_ap.dv.items():
            if next_ap.parent not in current_tree_node.visited_nodes:
                src_ap_idx = dict_ap_to_idx[current_ap]
                dest_ap_idx = dict_ap_to_idx[next_ap]

                # Create data copies
                path_copy = copy(current_path)
                mat_copy = current_mat.copy()

                # Visit dest_ap and mark src/dest row/col as infinity
                visit_cost = current_mat[src_ap_idx][dest_ap_idx]
                path_copy.append(next_ap)
                mark_as_visited(mat_copy, src_ap_idx, dest_ap_idx)

                # Reduce the matrix
                mat_copy, reduced_cost = reduce_matrix(mat_copy)

                next_cost = current_tree_node.cost + reduced_cost + visit_cost
                pq.enqueue(
                    TreeNode(
                        cost=next_cost,
                        path=path_copy,
                        matrix=mat_copy,
                        parent_tree_node=current_tree_node,
                    ),
                    next_cost,
                )
                # print(f"Enqueued {[ap.coord for ap in path_copy]}, Cost={next_cost}")
            else:
                pass


def setup_matrix(nodes: list[Node | SingleNode]):
    start_node = nodes[0]
    end_node = nodes[-1]

    # Multi Access
    # Initialize matrix and fill with infinite
    mat_size = len(nodes * 4)
    mat = np.full(shape=(mat_size, mat_size), fill_value=float("inf"))
    dict_ap_to_idx = {}  # Save mapping of APs -> row/col numbers.

    # Process item nodes
    for node in nodes:
        node_idx = nodes.index(node)
        rows_range = range(node_idx * 4, node_idx * 4 + 4)
        for r in rows_range:
            curr_ap = node.aps_all[r % 4]
            if curr_ap:  # Continue if current AP exists
                dict_ap_to_idx[curr_ap] = r  # Record this AP's row number for later use

                for c in range(0, mat_size):
                    dest_node = nodes[floor(c / 4)]
                    dest_ap = dest_node.aps_all[c % 4]

                    if (
                        node is not dest_node and dest_ap
                    ):  # Set grid to cost if destination AP exists
                        mat[r][c] = curr_ap.dv[dest_ap][0]
                        # print(f"({r},{c}) <== {mat[r][c]} ({dest_node.coord})")

    # Process start/end nodes
    start_node_range = range(0, 4)
    end_node_range = range(mat_size - 4, mat_size)

    # for r in start_node_range:
    #     for c in end_node_range:
    #         mat[r, c] = 0  # Start => End must be 0

    # for r in end_node_range:
    #     for c in start_node_range:
    #         mat[r, c] = float("inf")  # End => Start must be infinity

    # Copy the upper half to the lower half
    # row_indices, col_indices = np.triu_indices(mat_size, k=1)
    # for r, c in zip(row_indices, col_indices):
    #     mat[c, r] = mat[r, c]

    return mat, dict_ap_to_idx


def reduce_matrix(mat: np.ndarray):
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
    # print_matrix(compressed_mat)
    row_reduce_costs = [
        (min(row) if min(row) != float("inf") else 0) for row in compressed_mat
    ]
    for r, cost in enumerate(row_reduce_costs):
        # print(f"Reducing rows {r*4} ~ {(r+1)*4} by {cost}")
        # print(mat[r * 4 : (r + 1) * 4])
        # if cost != float("inf"):
        mat[r * 4 : (r + 1) * 4] -= cost
        # print(mat[r * 4 : (r + 1) * 4])
    # print(f"Row reduced cost = {sum(row_reduce_costs)}")

    # Reduce by col
    compressed_mat = compress_minimum_matrix(mat)
    # print_matrix(compressed_mat)
    col_reduce_costs = [
        (min(col) if min(col) != float("inf") else 0) for col in compressed_mat.T
    ]
    for c, cost in enumerate(col_reduce_costs):
        # print(f"Reducing cols {c*4} ~ {(c+1)*4} by {cost}")
        # print(mat[:, c * 4 : (c + 1) * 4])
        mat[:, c * 4 : (c + 1) * 4] -= cost
        # print(mat[:, c * 4 : (c + 1) * 4])
    # print(f"Column reduced cost = {sum(col_reduce_costs)}")

    total_cost = sum(row_reduce_costs) + sum(col_reduce_costs)
    # print(f"Finished reducing matrix. Cost = {total_cost}")
    # print_matrix(compress_minimum_matrix(mat))
    return mat, total_cost


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
