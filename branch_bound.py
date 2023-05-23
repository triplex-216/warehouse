# Input: map, pd_list
import numpy as np
import random
from lib.core import *


# generate original cost matrix
def generate_matrix(map, pd_list):

    # Matrix index : index = i * 4 + j
    # i: product index in pd_list
    # j: 0: Up 1: Down 2: Right 3: Left
    dir = [(0, 1), (0, -1), (1, 0), (-1, 0)]
    row, col = len(map), len(map[0])
    length = len(pd_list) * 4
    
    # Set all original costs to -1
    # If there exist neighbor, replace it with real cost calculated later
    ori_matrix = np.ones((length, length), dtype = int) * -1
    
    # Find neighbors
    def find_neighbors(node):
        neighbors = []
        neighbors_index = []
        for x, y in dir:
            neighbor = (node[0] + x, node[1] + y)
            if (
                neighbor[0] in range(row)
                and neighbor[1] in range(col)
                and map[neighbor[0]][neighbor[1]] == 0
            ):
                neighbors.append(neighbor)
                neighbors_index.append(dir.index((x,y)))
        return neighbors, neighbors_index
    
    # Get all neighbors and their index in the matrix
    pd_neighbors = []
    pd_neighbors_index = []   
    for i in range(len(pd_list)):
        neighbors, neighbors_index = find_neighbors(pd_list[i])
        pd_neighbors += neighbors
        for j in neighbors_index:
            index = i * 4 + j
            pd_neighbors_index.append(index)
    
    # Replace with real cost
    for i in range(len(pd_neighbors)):
        node1 = pd_neighbors[i]
        for j in range(len(pd_neighbors)):
            node2 = pd_neighbors[j]
            # Replace it with the function that calculate the true distance between 2 nodes
            real_cost = cost(node1, node2)
            ori_matrix[pd_neighbors_index[i]][pd_neighbors_index[j]] = real_cost

    # Avoid the cost between the node and itself
    np.fill_diagonal(ori_matrix, -1)

    return ori_matrix

# Only for test
def cost(x,y):
    return abs(x[0] - y[0]) + abs(x[1] - y[1])

def find_minimum_row_positive(row):
    min_positive = None
    
    for num in row:
        if (num > 0 or num == 0) and (min_positive is None or num < min_positive):
            min_positive = num
    
    # avoid return None
    if min_positive == None:
        min_positive = 0

    return min_positive

def find_minimum_col_positive(matrix, column_index):
    min_positive = None

    for row in matrix:
        num = row[column_index]
        if (num > 0 or num == 0) and (min_positive is None or num < min_positive):
            min_positive = num

    # avoid return None
    if min_positive == None:
        min_positive = 0

    return min_positive

# Calculate the reduced cost of the input matrix
def reduced_cost(matrix):
          
    [rows, cols] = matrix.shape

    row_cost =[]
    row_matrix = None
    for i in range(rows):
        value = find_minimum_row_positive(matrix[i])
        single_row = matrix[i] - value
        row_cost.append(value)

        if row_matrix is None:
            row_matrix = single_row
        else:
            row_matrix = np.vstack((row_matrix, single_row))
  

    reduced_matrix = row_matrix
    col_cost = []
    for i in range(cols):
        value = find_minimum_col_positive(reduced_matrix, i)
        col_cost.append(value)
        if value != 0:
            for row in reduced_matrix:
                row[i] -= value
    
    return sum(row_cost) + sum(col_cost), reduced_matrix

# Calculate the value of (node1, node2) + ReducedCost(node1, node2)
def nodes_cost(matrix, current, x):
    value = matrix[current][x]
    
    # Set it to all negative
    matrix[current, :] = -1  # Set entire row to -1
    matrix[:, x] = -1  # Set entire column to -1

    # Get reduce_cost between two nodes
    reduce_cost, _ = reduced_cost(matrix)

    return reduce_cost + value

# Find the shortest path from a specific start point
def single_path(ori_reduced_matrix, start_index, single_start):

    # Create index set 
    unvisited = set(range(len(ori_reduced_matrix)))

    # Create a copy
    copy_matrix = np.copy(ori_reduced_matrix)
    
    # Remove invalid index
    for i in range(len(ori_reduced_matrix)):
        if np.all(copy_matrix[i, :] < 0):
            unvisited.remove(i)
        # Remove other start_index
        elif i in start_index and i != single_start:
            unvisited.remove(i)
            # Set it to all negative
            copy_matrix[i, :] = -1  # Set entire row to -1
            copy_matrix[:, i] = -1  # Set entire column to -1
    
    current = single_start
    path = [current]
    path_cost = 0
    unvisited.remove(current)

    while unvisited:
        nearest = min(unvisited, key=lambda x: nodes_cost(copy_matrix, current, x))

        # Update the path
        path.append(nearest)
        # Update the path_cost
        path_cost += nodes_cost(copy_matrix, current, nearest)
        # Update the copy_matrix
        copy_matrix[current, :] = -1

        # Remove nearest node's neighbors
        i = nearest // 4
        for j in range(4):
            if i * 4 + j in unvisited:
                unvisited.remove(i * 4 +j)
                # Update the copy_matrix
                copy_matrix[:, i * 4 + j] = -1

        current = nearest

    # Return to the original start
    path.append(single_start)

    return path, path_cost

# Find the shortest path from a random start node's all possible neighbors
def find_shortest_route(map, pd_list):
    
    # Get ori_matrix
    ori_matrix = generate_matrix(map, pd_list)
    
    # Get ori_reduced_matrix and reduced cost(main)
    main_reduced_cost, ori_reduced_matrix = reduced_cost(ori_matrix)
    
    pd_id = len(pd_list)
    # Set a random start point
    start = random.randint(0, pd_id - 1)
    
    start_index = []
    for i in range(4):
        row_index = start * 4 + i
        if np.any(ori_reduced_matrix[row_index, :] >= 0):
            start_index.append(row_index) 
    
    # Get shortest path
    shortest_path = None
    shortest_path_cost = None
    for index in start_index:
        path, cost = single_path(ori_reduced_matrix, start_index, index)
        if shortest_path_cost == None or cost < shortest_path_cost:
            shortest_path_cost = cost
            shortest_path = path

    # Total cost
    total_cost = main_reduced_cost + shortest_path_cost

    return shortest_path, total_cost

# Print the detailed path direction
def print_path(path):
    node_num = []
    node_dir = []
    for i in range(len(path)):
        node_num.append(path[i] // 4)
        x = path[i] % 4
        # 0: Up 1: Down 2: Right 3: Left
        if x == 0:
            node_dir.append("North")
        elif x == 1:
            node_dir.append("South")
        elif x == 2:
            node_dir.append("East")
        elif x == 3:
            node_dir.append("West")

    for i in range(len(path) - 1):
        print(f"node {node_num[i]} {node_dir[i]} -->", end='')
    
    print(f"node {node_num[-1]} {node_dir[-1]}")

map_data, _ = read_inventory_data("data/qvBox-warehouse-data-s23-v01.txt")
pd_list = [(0,0), (10, 6), (12, 6), (10, 14), (20, 10)]
path, _ = find_shortest_route(map_data, pd_list)
print_path(path)