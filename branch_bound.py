# Input: map, pd_list
import numpy as np
import random
from lib.core import *
from lib.route import *


# generate original cost matrix
def generate_matrix(map, pd_list):

    # Matrix index : index = i * 4 + j
    # i: product index in pd_list
    # j: 0: South 1: North 2: West 3: East
    dir = [(0, -1), (0, 1), (-1, 0), (1, 0)]
    row, col = len(map), len(map[0])
    length = len(pd_list) * 4
    
    # Set all original costs to -1
    # If there exist neighbor, replace it with real cost calculated later
    ori_matrix = np.ones((length, length)) * float("inf")
    
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
            ret = cost(map, node1, node2)
            real_cost = ret[0]
            # real_cost = cost(map, node1, node2)[0]
            ori_matrix[pd_neighbors_index[i]][pd_neighbors_index[j]] = real_cost

    # Avoid the cost between the node and itself
    for i in range(len(pd_list)):
        index1 = i * 4
        index2 = (i + 1) * 4
        for x in range(index1, index2):
            for y in range(index1, index2):
                ori_matrix[x][y] = float("inf")
    return ori_matrix

def find_minimum_row(row):
    min_value = min(row)
    
    # avoid return infinity
    if min_value == float("inf"):
        min_value = 0

    return min_value

def find_minimum_col(matrix, column_index):
    min_value = float("inf")

    for row in matrix:
        if row[column_index] < min_value:
            min_value = row[column_index]

     # avoid return infinity
    if min_value == float("inf"):
        min_value = 0
    return min_value

# Calculate the reduced cost of the input matrix
def reduced_cost(matrix):
          
    [rows, cols] = matrix.shape
    
    row_matrix = np.copy(matrix)
    row_cost =[]
    for i in range(rows):
        value = find_minimum_row(row_matrix[i])
        row_matrix[i] -= value
        row_cost.append(value)

    reduced_matrix = np.copy(row_matrix)
    col_cost = []
    for i in range(cols):
        value = find_minimum_col(reduced_matrix, i)
        col_cost.append(value)
        #if value != 0:
        for row in reduced_matrix:
            row[i] -= value
    
    return sum(row_cost) + sum(col_cost), reduced_matrix

# Calculate the value of (node1, node2) + ReducedCost(node1, node2)
def nodes_cost(matrix, current, x):
    value = matrix[current][x]
    # Make a copy of the matrix
    copy_matrix = np.copy(matrix)
    # Set it to all infinity
    copy_matrix[current, :] = float("inf")
    copy_matrix[:, x] = float("inf")

    # Get reduce_cost between two nodes
    reduce_cost, _ = reduced_cost(copy_matrix)

    return reduce_cost + value

# Find the shortest path from a specific start point
def single_path(ori_reduced_matrix, start_index, single_start):

    # Create index set 
    unvisited = set(range(len(ori_reduced_matrix)))

    # Create a copy
    copy_matrix = np.copy(ori_reduced_matrix)
    
    # Remove invalid index
    for i in range(len(ori_reduced_matrix)):
        if np.all(copy_matrix[i, :] == float("inf")):
            unvisited.remove(i)
        # Remove other start_index
        elif i in start_index and i != single_start:
            unvisited.remove(i)
            # Set it to all infinity
            copy_matrix[i, :] = float("inf")  
            copy_matrix[:, i] = float("inf")  
    
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
        copy_matrix[current, :] = float("inf")
        copy_matrix[:, nearest] = float("inf")

        # Remove nearest node's neighbors
        i = nearest // 4
        for j in range(4):
            neighbor_index = i * 4 + j
            if neighbor_index in unvisited and neighbor_index != nearest:
                unvisited.remove(i * 4 + j)
                # Update the copy_matrix
                copy_matrix[i * 4 + j, :] = float("inf")
                copy_matrix[:, i * 4 + j] = float("inf")
        
        unvisited.remove(nearest)
        current = nearest

    # Return to the original start
    path.append(single_start)

    return path, path_cost

# Find the shortest path from a random start node's all possible neighbors
def branch_and_bound(map, pd_list):
    drift = []
    node_num = []
    coord_route = []
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
        if min(ori_reduced_matrix[row_index, :]) == 0:
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

    for i in range(len(shortest_path)):
        node_num.append(shortest_path[i] // 4)
        x = shortest_path[i] % 4
        if x == 0:
            drift.append([0, -1])
        elif x == 1:
            drift.append([0, 1])
        elif x == 2:
            drift.append([-1, 0])
        elif x == 3:
            drift.append([1, 0])
    
    
    for i in range(len(shortest_path)):
        x = pd_list[node_num[i]][0] + drift[i][0]
        y = pd_list[node_num[i]][1] + drift[i][1]

        if (x,y) == (1,0) or (x,y) == (0,1):
            coord_route.append((0, 0))

        coord_route.append((x,y))

    return total_cost, coord_route


# map_data, prod_db = read_inventory_data("data/qvBox-warehouse-data-s23-v01.txt")
# pd_list = [(0,0), (2, 0), (8, 14), (6, 6), (11, 8), (10, 6), (8, 8), (12, 10), (16, 8), (16, 4), (14, 8), (6, 14), (8, 6), (20, 14)]
# # pd_list = [(0, 0), (10, 6), (10, 14), (12, 6), (20, 10)]
# path, _ = find_shortest_route(map_data, pd_list)
# distance, route = path_to_route(map_data, path)
# print(f"Total distance is {distance}.")
# print(get_instructions(route, prod_db, pd_list))
