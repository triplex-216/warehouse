# Input: map, pd_list
import numpy as np
import random
from lib.core import *
from lib.route import *

# Find the shortest path from a random start node's all possible neighbors
def branch_and_bound(map, pd_list):
    
    # Get ori_matrix
    ori_matrix = generate_matrix(map, pd_list)
    
    # Get ori_reduced_matrix and reduced cost(main)
    main_reduced_cost, ori_reduced_matrix = reduced_cost(ori_matrix)

    
    # Set a random start point
    start = random.randint(0, len(pd_list) - 1)
    #start = 0
    print(start)
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

    drift = []
    node_num = []
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
    

    coord_route = []
    for i in range(len(shortest_path)):
        x = pd_list[node_num[i]][0] + drift[i][0]
        y = pd_list[node_num[i]][1] + drift[i][1]

        if (x,y) == (0, -1):
            coord_route.append((0, 0))
        else:
            coord_route.append((x,y))
    
    # print(coord_route)

    # make (0,0) as start
    # if coord_route[0] == (0,0):
    #    final_path = coord_route
    # else:
    #    index = coord_route.index((0,0))
    #    final_path = coord_route[index:-1] + coord_route[:index]
    #    final_path.append((0,0))

    return coord_route, total_cost

map_data, _ = read_inventory_data("data/qvBox-warehouse-data-s23-v01.txt")
pd_list = [(0,0), (2, 0), (8, 14), (6, 6), (11, 8), (10, 6), (8, 8)]
# pd_list = [(0, 0), (10, 6), (10, 14), (12, 6), (20, 10)]
path, b= branch_and_bound(map_data, pd_list)
print(path, b)