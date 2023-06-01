# Input: map, pd_list
import numpy as np
import random
from lib.core import *
from lib.route import *

# generate original cost matrix
def single_generate_matrix(map, pd_list):

    length = len(pd_list) 
    
    # Set all original costs to infinity
    ori_matrix = np.ones((length, length)) * float("inf")
    
    # Copy map for calculate distance
    copy_map = map.copy()
    for node in pd_list:
        x = node[0]
        y = node[1]
        copy_map[x][y] = 0

    # Replace with real cost
    for i in range(length):
        node1 = pd_list[i]
        for j in range(length):
            node2 = pd_list[j]
            # Replace it with the function that calculate the true distance between 2 nodes
            ret = cost(copy_map, node1, node2)
            real_cost = ret[0]
            ori_matrix[i][j] = real_cost

    # Avoid the cost between the node and itself
    np.fill_diagonal(ori_matrix, float("inf"))

    return ori_matrix

# Find the shortest path from a specific start point
def single_access_path(ori_reduced_matrix, single_start):

    # Create index set 
    unvisited = set(range(len(ori_reduced_matrix)))

    # Create a copy
    copy_matrix = np.copy(ori_reduced_matrix)
    
    current = single_start
    path = [current]
    path_cost = 0
    # unvisited.remove(current)

    temp_path = []
    while len(path) < len(ori_reduced_matrix):
        visted = set(path)
        copy_set = unvisited.copy()
        for node in copy_set:
            if node not in visted:
                # Make a copy
                copy_path = list(path)
                copy_matrix_2 = np.copy(copy_matrix)

                copy_path.append(node)
                cur_cost = current_cost(copy_matrix_2, copy_path)
                heapq.heappush(temp_path, (cur_cost, copy_path))

        cur_shortest_path = heapq.heappop(temp_path)
        path_cost = cur_shortest_path[0]
        path = cur_shortest_path[1]

    # Return to the original start
    path.append(single_start)

    return path, path_cost

def single_branch_and_bound(map, pd_list):
    
    # Get ori_matrix
    ori_matrix = single_generate_matrix(map, pd_list)
    
    # Get ori_reduced_matrix and reduced cost(main)
    main_reduced_cost, ori_reduced_matrix = reduced_cost(ori_matrix)
    
    # Set a random start point
    start = random.randint(0, len(pd_list) - 1)
    
    # Get shortest path
    shortest_path, shortest_path_cost = single_access_path(ori_reduced_matrix, start)

    # Total cost
    total_cost = main_reduced_cost + shortest_path_cost
    
    coord_route = []
    for i in range(len(shortest_path)):
        coord_route.append(pd_list[shortest_path[i]])
     
    # Re-arrange the order and make (0,0) as start
    if coord_route[0] == (0,0):
        final_path = coord_route
    else:
        index = coord_route.index((0,0))
        final_path = coord_route[index:-1] + coord_route[:index]
        final_path.append((0,0))

    return final_path, total_cost


map_data, _ = read_inventory_data("data/qvBox-warehouse-data-s23-v01.txt")
#pd_list = [(0,0), (2, 0), (8, 14), (6, 6), (11, 8), (10, 6), (8, 8), (12, 10), (16, 8), (16, 4), (14, 8), (6, 14), (8, 6), (20, 14)]
pd_list = [(0, 0), (7, 8), (8, 8), (10, 6), (12, 6), (10, 10), (10, 12)]
#pd_list = [(0, 0), (10, 6), (10, 14), (12, 6), (20, 10)]
path, b = single_branch_and_bound(map_data, pd_list)
print(path, b)