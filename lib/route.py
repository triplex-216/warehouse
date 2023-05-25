import heapq
from .core import get_item, get_item_locations


def cost(map, start, end):
    """
    calculate distance between two single node
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
            route.append(start)
            return (len(route), route[::-1])

        # Check each neighbor of the current node
        for neighbor in get_neighbors(map, current_node):
            # Calculate the tentative cost to reach the neighbor
            tentative_dis = distance[current_node] + 1
            # If the neighbor is not in the open set or the tentative cost is less than the existing cost, add it to the open set
            if tentative_dis < distance.get(neighbor, float("inf")):
                distance[neighbor] = tentative_dis
                heapq.heappush(visited_set, (tentative_dis, neighbor))
                parent[neighbor] = current_node

    return -1

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


def get_distance(map, start_node, end_node):
    """
    get the distance between all accessible entries of two products
    """
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


def get_graph(map, nodes):
    graph = {}
    for i in range(len(nodes)):
        for j in range(i + 1, len(nodes)):
            dis = get_distance(map, nodes[i], nodes[j])
            graph = {**graph, **dis}
    return graph


def greedy(map, prod_db, item_ids, start=(0, 0)) -> tuple[int, list[tuple[int, int]]]:
    """
    give a list of item to be fetched, return the greedy route
    """
    all_nodes = [start] + get_item_locations(prod_db, item_ids)
    items = get_item(prod_db, item_ids)
    graph = get_graph(map, all_nodes)

    visited = {start}
    path = [start]
    route = []
    total_cost = 0

    all_neighbors = []
    parent = {}
    parent[start] = start

    while items:
        current = path[-1]
        nearest_neighbor = None
        nearest_distance = float("inf")

        for item in items:
            for neighbor in item.neighbors():
                try:
                    dist, trace = graph[(current, neighbor)]
                except KeyError:
                    dist, trace = (
                        graph[(neighbor, current)][0],
                        graph[(neighbor, current)][1][::-1],
                    )

                if not dist:
                    break

                if neighbor not in visited and dist < nearest_distance:
                    nearest_neighbor = neighbor
                    nearest_distance = dist
                    nearest_trace = trace

        if nearest_neighbor is not None:
            path.append(nearest_neighbor)
            route += nearest_trace[:-1]
            total_cost += nearest_distance
            visited.add(nearest_neighbor)
            # i = orig_neighbors.index(nearest_neighbor_group)
            # parent[nearest_neighbor] = all_nodes[i+1]
            for item in items:
                if nearest_neighbor in item.neighbors():
                    items.remove(item)
        else:
            # No unvisited neighbors found, the graph might be disconnected
            break

    # Add the start node to complete the cycle
    route += graph[(start, path[-1])][1][::-1]
    total_cost += graph[(start, path[-1])][0]

    path.append(start)
    print(path)
    print(route)
    return total_cost, route

def default(map, prod_db, item_ids, start=(0, 0)):
    items = get_item(prod_db, item_ids)
    path = [start]
    for item in items:
        path.append(item.neighbors()[0])
    path.append(start)
    return path_to_route(map, path)

def path_to_route(map, path):
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
            dir = "down"
        elif position[0] < next_position[0]:
            dir = "up"
        elif position[1] > next_position[1]:
            dir = "left"
        elif position[1] < next_position[1]:
            dir = "right"

        return dir

    def is_prod_entry(pos):
        pickup = []
        for item in items:
            if pos in item.neighbors():
                pickup.append(item.id)
                items.remove(item)
        return pickup

    def rev(pos: tuple[int, int]) -> tuple[int, int]:
        return (pos[1], pos[0])

    # if there are only one node in the route
    if len(route) == 1:
        instruction_str += "You can pick up the product at current position!\n"
        return

    start, next_pos = route[0], route[1]
    instruction = get_step_instruction(start, next_pos)
    dis = 1

    for idx in range(1, len(route) - 1):
        pos, next_pos = route[idx], route[idx + 1]
        new_instruction = get_step_instruction(pos, next_pos)
        pickup = is_prod_entry(pos)
        if pickup:
            instruction_str += f"From {rev(start)} move {dis} {'steps' if dis > 1 else 'step'} {instruction} to {rev(pos)}\n"
            instruction_str += f"Pick up the product {pickup}!\n"
            instruction = new_instruction
            start = pos
            dis = 1
        else:
            # if two idr are the same
            if new_instruction == instruction:
                dis += 1
            else:
                instruction_str += f"From {rev(start)} move {dis} {'steps' if dis > 1 else 'step'} {instruction} to {rev(pos)}\n"
                instruction = new_instruction
                start = pos
                dis = 1
    instruction_str += f"From {rev(start)}, move {dis} {'steps' if dis > 1 else 'step'} {instruction} to {rev(next_pos)}\n"
    instruction_str += "Return to the start position!\n"

    return instruction_str


def bb(map, prod_db, item_ids, start=(0, 0)) -> tuple[int, list[tuple[int, int]]]:
    pass


def fallback(map, prod_db, item_ids, start=(0, 0)) -> tuple[int, list[tuple[int, int]]]:
    pass


def find_route(map, prod_db, start, item_ids, algorithm="g"):
    if algorithm == "b":  # branch and bound
        total_cost, route = bb(map=map, prod_db=prod_db, item_ids=item_ids, start=start)
    elif algorithm == "g":  # greedy
        total_cost, route = greedy(
            map=map, prod_db=prod_db, item_ids=item_ids, start=start
        )
    elif algorithm == "f":  # fallback
        total_cost, route = fallback(
            map=map, prod_db=prod_db, item_ids=item_ids, start=start
        )

    return route
