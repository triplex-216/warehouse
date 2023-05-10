import heapq


def find_route(map, start, end):
    dir = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    row, col = len(map), len(map[0])
    # Initialize the distance dictionary with the starting node and a cost of 0
    distance = {start: 0}
    # Initialize the priority queue with the starting node and its cost
    open_set = [(0, start)]
    # Initialize the closed(visited) set as an empty set
    closed_set = set()
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

    end_positions = get_neighbors(end)

    while open_set:
        # Get the node with the lowest cost from the priority queue
        current_node = heapq.heappop(open_set)[1]

        if current_node in end_positions:
            while current_node in parent:
                route.append(current_node)
                current_node = parent[current_node]
            route.append(start)
            return route[::-1]

        # Add the current node to the closed set
        closed_set.add(current_node)
        # Check each neighbor of the current node
        for neighbor in get_neighbors(current_node):
            # Calculate the tentative cost to reach the neighbor
            tentative_dis = distance[current_node] + 1
            # If the neighbor is not in the open set or the tentative cost is less than the existing cost, add it to the open set
            if tentative_dis < distance.get(neighbor, float("inf")):
                distance[neighbor] = tentative_dis
                heapq.heappush(open_set, (tentative_dis, neighbor))
                parent[neighbor] = current_node

    # If we've exhausted all possible paths and haven't reached the end node, return None
    return None


def get_step_instruction(position, next_position):
    """
    get route discription of one movement
    """
    # get vertical direction
    if position[0] > next_position[0]:
        dir = "down"
    elif position[0] < next_position[0]:
        dir = "up"
    elif position[1] > next_position[1]:
        dir = "left"
    elif position[1] < next_position[1]:
        dir = "right"

    return dir


def print_instructions(route, back):
    """
    get instructions of a given route
    """
    if len(route) == 1:
        if not back:
            print("You can pick up the product at current position!")
        return
    start, next_pos = route[0], route[1]
    instruction = get_step_instruction(start, next_pos)
    dis = 1
    for idx in range(1, len(route) - 1):
        pos, next_pos = route[idx], route[idx + 1]
        new_instruction = get_step_instruction(pos, next_pos)
        if new_instruction == instruction:
            dis += 1
        else:
            print(
                f"From {(start[1], start[0])} move {dis} {'steps' if dis > 1 else 'step'} {instruction} to {(pos[1], pos[0])}"
            )
            instruction = new_instruction
            start = pos
            dis = 1
    print(
        f"From {(start[1], start[0])}, move {dis} {'steps' if dis > 1 else 'step'} {instruction} to {(next_pos[1], next_pos[0])}"
    )
    if back:
        print("Return to the start position.")
    else:
        print("Pick up the product!")
