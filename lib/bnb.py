from __future__ import annotations
import numpy as np
from .route import Node, SingleNode, AccessPoint
from random import choice
from math import floor
from copy import deepcopy, copy
from numba import jit, njit, prange

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

    def enqueue(self, item, priority1, priority2):
        heapq.heappush(self._queue, (priority1, priority2, self._index, item))
        self._index += 1

    def dequeue(self):
        if self.is_empty():
            raise IndexError("Priority queue is empty")
        _, _, _, item = heapq.heappop(self._queue)
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
    nodes: list[Node | SingleNode],
    start_ap: AccessPoint,
    end_ap: AccessPoint,
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

        # for r in range(dest_node_idx * 4, (dest_node_idx + 1) * 4):
        #     if r != dest_ap_idx:
        #         mat[r] = float("inf")

        return mat

    # 1. Setup the initial matrix and reduce
    init_mat, dict_ap_to_idx = setup_matrix(nodes=nodes)
    # print_matrix(init_mat)
    init_mat, init_reduced_cost = reduce_matrix(init_mat)
    # print_matrix(init_mat)
    # 3. Start branching
    # Randomly pick an ap
    init_node = choice(nodes)
    # init_node = nodes[0]
    print(f"Initializing BnB @ {init_node.coord}")
    init_aps = init_node.aps

    pq = PriorityQueue()

    for ap in init_aps:
        path = [ap]
        pq.enqueue(
            TreeNode(
                cost=init_reduced_cost,
                path=[ap],
                matrix=init_mat,
                parent_tree_node=None,
            ),
            priority1=init_reduced_cost,
            priority2=1 / len(path),
        )

    best_tree_node = None

    while pq:
        current_tree_node: TreeNode
        current_tree_node = pq.dequeue()
        current_ap = current_tree_node.path[-1]

        current_path = current_tree_node.path
        current_mat = current_tree_node.matrix
        init_ap = current_path[0]
        next_aps = []
        # Check if all nodes have been visited
        if len(current_tree_node.path) == len(nodes) + 1:
            best_tree_node = current_tree_node
            return best_tree_node.cost, best_tree_node.path[:-1]
        elif len(current_tree_node.path) == len(nodes):
            next_aps = [init_ap]  # add back route
        else:
            for ap in current_ap.dv.keys():
                if ap.parent != init_ap.parent:
                    next_aps.append(ap)

        for next_ap in next_aps:
            src_ap_idx = dict_ap_to_idx[current_ap]
            dest_ap_idx = dict_ap_to_idx[next_ap]
            visit_cost = current_mat[src_ap_idx][dest_ap_idx]
            if visit_cost != float("inf"):
                # Create data copies
                path_copy = copy(current_path)
                mat_copy = current_mat.copy()

                # Visit dest_ap and mark src/dest row/col as infinity
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
                    1 / len(path_copy),
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

    return mat, dict_ap_to_idx

@jit(nopython=True)
def reduce_matrix(mat: np.ndarray):
    mat_size = mat.shape[0]

    # Reduce by row
    row_reduce_costs = 0
    for i in range(int(mat_size / 4)):
        row_reduced = mat[i * 4 : i * 4 + 4, :].min()
        if row_reduced != np.inf:
            row_reduce_costs += row_reduced
            mat[i * 4 : i * 4 + 4, :] -= row_reduced

    col_reduce_costs = 0
    for i in range(int(mat_size / 4)):
        col_reduced = mat[:, i * 4 : i * 4 + 4].min()
        if col_reduced != np.inf:
            col_reduce_costs += col_reduced
            mat[:, i * 4 : i * 4 + 4] -= col_reduced

    total_cost = row_reduce_costs + col_reduce_costs
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
