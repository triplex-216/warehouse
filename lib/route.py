import heapq
import numpy as np
import random
from .core import get_item, get_item_locations

# generate original cost matrix
def generate_matrix(map, pd_list):

    # Matrix index : index = i * 4 + j 
    # i: product index in pd_list
    # j: 0: South 1: North 2: West 3: East
    dir = [(0, -1), (0, 1), (-1, 0), (1, 0)]
    col, row = len(map), len(map[0])
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
def branch_and_bound(graph, items, start=(0,0), end=(0,0)):
    drift = []
    node_num = []
    coord_route = []
    all_nodes = [start] + items + [end]
    # Get ori_matrix
    ori_matrix = generate_matrix(graph, all_nodes)
    
    # Get ori_reduced_matrix and reduced cost(main)
    main_reduced_cost, ori_reduced_matrix = reduced_cost(ori_matrix)

    pd_id = len(all_nodes)
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
        x = all_nodes[node_num[i]][0] + drift[i][0]
        y = all_nodes[node_num[i]][1] + drift[i][1]

        if (x,y) == (1,0) or (x,y) == (0,1):
            coord_route.append((0, 0))
        else:
            coord_route.append((x,y))

    # make (0,0) as start
    if coord_route[0] == (0,0):
        final_path = coord_route
    else:
        index = coord_route.index((0,0))
        final_path = coord_route[index:-1] + coord_route[:index]
        final_path.append((0,0))

    total_cost, route = path_to_route(map, final_path)

    return total_cost, route

def cost(map, start, end):
    """
    calculate distance and shortest route between two single entries
    """
    parent = {}
    route = []
    # Initialize the distance dictionary with the starting node and a cost of 0
    distance = {start: 0}
    # Initialize the priority queue with the starting node and its cost
    visited_set = [(0, start)]
    while visited_set:
        # Get the node with the lowest cost from the priority queue
        current_node = heapq.heappop(visited_set)[1]

        if current_node == end:
            while current_node in parent:
                route.append(current_node)
                current_node = parent[current_node]
            # append route with start node
            route.append(start)
            costs = len(route) - 1
            return (costs, route[::-1])

        # Check each neighbor of the current node
        for neighbor in get_neighbors(map, current_node):
            # Calculate the tentative cost to reach the neighbor
            tentative_dis = distance[current_node] + 1
            # If the neighbor is not in the open set or the tentative cost is less than the existing cost, add it to the open set
            if tentative_dis < distance.get(neighbor, float("inf")):
                distance[neighbor] = tentative_dis
                heapq.heappush(visited_set, (tentative_dis, neighbor))
                parent[neighbor] = current_node

    print(f"Can not get to position{end}, check if it is a shelf!")
    return None

def get_neighbors(map, node):
    neighbors = []
    dir = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    row, col = len(map), len(map[0])
    for d_x, d_y in dir:
        neighbor = (node[0] + d_x, node[1] + d_y)
        if (
            neighbor[0] in range(row)
            and neighbor[1] in range(col)
            and map[neighbor[0]][neighbor[1]] == 0
        ):
            neighbors.append(neighbor)

    return neighbors


def get_distance(map, node1, node2, start=(0,0), end=(0,0)):
    """
    get the dictionary records the distances between all accessible entries of two nodes
    """
    dis = {}
    if node1 == start or node1 == end:
        positions1 = [node1]
    else:
        positions1 = node1.neighbors()
    
    if node2 == start or node2 == end:
        positions2 = [node2]
    else:
        positions2 = node2.neighbors()

    for p1 in positions1:
        for p2 in positions2:
            if p1 and p2:
                distance, route = cost(map, p1, p2)
                dis[(p1, p2)] = (distance, route)
                dis[(p2, p1)] = (distance, route[::-1])

    return dis


def get_graph(map, nodes, start=(0,0), end=(0,0)):
    """
    get the whole graph(distance and route) of every product pair
    """
    graph = {}
    for i in range(len(nodes)):
        for j in range(i + 1, len(nodes)):
            dis = get_distance(map, nodes[i], nodes[j], start, end)
            graph = {**graph, **dis}
    return graph


def greedy(graph, items, start=(0, 0), end=(0,0)) -> tuple[int, list[tuple[int, int]]]:
    """
    give a list of item to be fetched, return the greedy route
    """
    route = [start]
    total_cost = 0

    while items:
        current = route[-1]
        nearest_neighbor = None
        nearest_distance = float("inf")
        # search every neighbors of unvisited items
        for item in items:
            for neighbor in item.neighbors():
                if neighbor and neighbor not in route:
                    dist, trace = graph[(current, neighbor)]

                    if dist < nearest_distance:
                        nearest_neighbor = neighbor
                        nearest_distance = dist
                        nearest_trace = trace

        if nearest_neighbor:
            route += nearest_trace[1:]
            total_cost += nearest_distance
            # remove visited item in items list
            for item in items:
                if nearest_neighbor in item.neighbors():
                    items.remove(item)
        else:
            # No unvisited neighbors found, the graph might be disconnected
            break

    # Add the back route to complete the cycle
    back_cost, back_route = graph[(route[-1], end)]
    total_cost += back_cost
    route += back_route[1:]

    return total_cost, route

def default(graph, items, start=(0, 0), end=(0,0)):
    route = [start]
    total_cost = 0
    visited = {start}

    for item in items:
        # add visited item
        for neighbor in item.neighbors():
            if neighbor in route:
                visited.add(item)
                break

        if item not in visited:
            # set entry as the first not None neighbor
            for neighbor in item.neighbors():
                if neighbor:
                    entry = neighbor
                    break
            cost, trace = graph[(route[-1], entry)]
            route += trace[1:]
            total_cost += cost
    
    # Add the back route to complete the cycle
    back_cost, back_route = graph[(route[-1], end)]
    total_cost += back_cost
    route += back_route[1:]

    return total_cost, route

def path_to_route(map, path: list[tuple]):
    """
    Transfer path to route with every passed node contained
    """
    total_cost = 0
    route = []
    pos = path[0]
    for next_pos in path[1:]:
        dis, trace = cost(map, pos, next_pos)
        total_cost += dis
        route += trace[:-1]
        pos = next_pos
    route.append(path[-1])

    return total_cost, route

def get_instructions(route: list, prod_db: dict, item_ids: list):
    """
    get instructions of a given route
    """

    instruction_str = ""
    items = get_item(prod_db, item_ids)

    def get_step_instruction(position, next_position):
        """
        get route discription of one movement
        """
        # get direction
        if position[0] > next_position[0]:
            dir = "left"
        elif position[0] < next_position[0]:
            dir = "right"
        elif position[1] > next_position[1]:
            dir = "down"
        elif position[1] < next_position[1]:
            dir = "up"

        return dir

    def is_prod_entry(pos):
        pickup = []
        for item in items:
            if pos in item.neighbors() and pos is not None:
                pickup.append(item.id)
                items.remove(item)
        return pickup

    # if there are only one node in the route
    if len(route) == 1:
        instruction_str += "You can pick up the product at current position!\n"
        return

    start, next_pos = route[0], route[1]
    instruction = get_step_instruction(start, next_pos)
    dis = 1
    cnt = 0

    for idx in range(1, len(route) - 1):
        pos, next_pos = route[idx], route[idx + 1]
        new_instruction = get_step_instruction(pos, next_pos)
        pickup = is_prod_entry(pos)
        cnt += len(pickup)
        if pickup:
            instruction_str += f"From {start} move {dis} {'steps' if dis > 1 else 'step'} {instruction} to {pos}\n"
            instruction_str += f"Pick up the product {pickup}!\n"
            instruction = new_instruction
            start = pos
            dis = 1
        else:
            # if two idr are the same
            if new_instruction == instruction:
                dis += 1
            else:
                instruction_str += f"From {start} move {dis} {'steps' if dis > 1 else 'step'} {instruction} to {pos}\n"
                instruction = new_instruction
                start = pos
                dis = 1
    instruction_str += f"From {start}, move {dis} {'steps' if dis > 1 else 'step'} {instruction} to {next_pos}\n"
    instruction_str += "Return to the start position!\n"

    return instruction_str

def find_route(map, prod_db, item_ids, start=(0,0), end=(0,0), algorithm="g"):
    # Calculate the graph(distance and route between all the accessible entries)
    items = get_item(prod_db, item_ids)
    all_nodes = [start] + items + [end]
    graph = get_graph(map, all_nodes)
    
    if algorithm == "b":  # branch and bound
        total_cost, route = branch_and_bound(map=map,items=items, start=start, end=end)
    elif algorithm == "g":  # greedy
        total_cost, route = greedy(
            graph=graph, items=items, start=start, end=end
        )
    elif algorithm == "f":  # fallback
        total_cost, route = default(
            graph=graph, items=items, start=start, end=end
        )
    
    return total_cost, route
