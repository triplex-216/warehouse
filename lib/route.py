import heapq


def get_neighbors(map, node):
    dir = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    row, col = len(map), len(map[0])
    neighbors = []
    for x, y in dir:
        neighbor = (node[0] + x, node[1] + y)
        if (
            neighbor[0] in range(row)
            and neighbor[1] in range(col)
            and map[neighbor[0]][neighbor[1]] == 0
        ):
            neighbors.append(neighbor)
    return neighbors


def cost(map, start, end):
    """
    calculate distance between two single node
    """
    # Initialize the distance dictionary with the starting node and a cost of 0
    distance = {start: 0}
    # Initialize the priority queue with the starting node and its cost
    visited_set = [(0, start)]
    while visited_set:
        # Get the node with the lowest cost from the priority queue
        current_node = heapq.heappop(visited_set)[1]

        if current_node == end:
            return distance[current_node]

        # Check each neighbor of the current node
        for neighbor in get_neighbors(map, current_node):
            # Calculate the tentative cost to reach the neighbor
            tentative_dis = distance[current_node] + 1
            # If the neighbor is not in the open set or the tentative cost is less than the existing cost, add it to the open set
            if tentative_dis < distance.get(neighbor, float("inf")):
                distance[neighbor] = tentative_dis
                heapq.heappush(visited_set, (tentative_dis, neighbor))


def get_distance(map, start_node, end_node):
    dis = {}
    if end_node == (0, 0):
        end_positions = [end_node]
    else:
        end_positions = get_neighbors(map, end_node)

    if start_node == (0, 0):
        start_positions = [start_node]
    else:
        start_positions = get_neighbors(map, start_node)

    for start in start_positions:
        for end in end_positions:
            dis[(start, end)] = cost(map, start, end)

    return dis


def find_route(map, start, end, adjacent=True):
    dir = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    row, col = len(map), len(map[0])
    # Initialize the distance dictionary with the starting node and a cost of 0
    distance = {start: 0}
    # Initialize the priority queue with the starting node and its cost
    visited_set = [(0, start)]
    # Keep track of the parent node for each node in the shortest path
    parent = {}
    route = []

    def get_neighbors(node):
        neighbors = []
        for x, y in dir:
            neighbor = (node[0] + x, node[1] + y)
            if (
                neighbor[0] in range(row)
                and neighbor[1] in range(col)
                and map[neighbor[0]][neighbor[1]] == 0
            ):
                neighbors.append(neighbor)
        return neighbors

    # If find path to adjacent grids, consider all the end grid's neighbors
    # Else only consider the end grid itself.
    if adjacent:
        end_positions = get_neighbors(end)
    else:
        end_positions = [end]

    while visited_set:
        # Get the node with the lowest cost from the priority queue
        current_node = heapq.heappop(visited_set)[1]

        if current_node in end_positions:
            while current_node in parent:
                route.append(current_node)
                current_node = parent[current_node]
            route.append(start)
            return route[::-1]

        # Check each neighbor of the current node
        for neighbor in get_neighbors(current_node):
            # Calculate the tentative cost to reach the neighbor
            tentative_dis = distance[current_node] + 1
            # If the neighbor is not in the open set or the tentative cost is less than the existing cost, add it to the open set
            if tentative_dis < distance.get(neighbor, float("inf")):
                distance[neighbor] = tentative_dis
                heapq.heappush(visited_set, (tentative_dis, neighbor))
                parent[neighbor] = current_node

    # If we've exhausted all possible paths and haven't reached the end node, return None
    return None


# def greedy(map, start, items):
#     """
#     give a list of item to be fetched, return the greedy route
#     """
#     graph = get_graph(map, items)
#     while items:

#     pass


def get_instructions(route, back):
    """
    get instructions of a given route
    """

    instruction_str = ""

    def get_step_instruction(position, next_position):
        """
        get route discription of one movement
        """
        # get direction
        if position[0] > next_position[0]:
            dir = "down"
        elif position[0] < next_position[0]:
            dir = "up"
        elif position[1] > next_position[1]:
            dir = "left"
        elif position[1] < next_position[1]:
            dir = "right"

        return dir

    # if there are only one node in the route
    if len(route) == 1:
        if not back:
            instruction_str += "You can pick up the product at current position!\n"
        return

    start, next_pos = route[0], route[1]
    instruction = get_step_instruction(start, next_pos)
    dis = 1

    for idx in range(1, len(route) - 1):
        pos, next_pos = route[idx], route[idx + 1]
        new_instruction = get_step_instruction(pos, next_pos)
        # if two idr are the same
        if new_instruction == instruction:
            dis += 1
        else:
            instruction_str += f"From {start} move {dis} {'steps' if dis > 1 else 'step'} {instruction} to {pos}\n"
            instruction = new_instruction
            start = pos
            dis = 1
    instruction_str += f"From {start}, move {dis} {'steps' if dis > 1 else 'step'} {instruction} to {next_pos[1]}\n"
    if back:
        instruction_str += "Return to the start position.\n"
    else:
        instruction_str += "Pick up the product!\n"

    return instruction_str
