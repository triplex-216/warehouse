import heapq
import copy
from .core import get_item, get_item_locations


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
            dist = distance[current_node]
            while current_node in parent:
                route.append(current_node)
                current_node = parent[current_node]
            route.append(start)
            return (dist, route[::-1])

        # Check each neighbor of the current node
        for neighbor in get_neighbors(map, current_node):
            # Calculate the tentative cost to reach the neighbor
            tentative_dis = distance[current_node] + 1
            # If the neighbor is not in the open set or the tentative cost is less than the existing cost, add it to the open set
            if tentative_dis < distance.get(neighbor, float("inf")):
                distance[neighbor] = tentative_dis
                heapq.heappush(visited_set, (tentative_dis, neighbor))
                parent[neighbor] = current_node


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


def greedy(map, prod_db, item_ids, start=(0, 0)):
    """
    give a list of item to be fetched, return the greedy route
    """
    all_nodes = [start] + get_item_locations(prod_db, item_ids)
    items = get_item(prod_db, item_ids)
    num_nodes = len(all_nodes)
    graph = get_graph(map, all_nodes)

    visited = {start}
    path = [start]
    route = []
    total_cost = 0

    all_neighbors = []
    parent = {}
    parent[start] = start

    for item in items:
        all_neighbors += [item.neighbors()]

    orig_neighbors = copy.deepcopy(all_neighbors)

    while len(path) < num_nodes:
        current = path[-1]
        nearest_neighbor = None
        nearest_distance = float("inf")

        for neighbor_group in all_neighbors:
            for neighbor in neighbor_group:
                try:
                    dist, trace = graph[(current, neighbor)] if graph[(current, neighbor)] else graph[(neighbor, current)]
                except KeyError:
                    pass

                if not dist:
                    break

                if (
                    neighbor not in visited
                    and neighbor not in get_neighbors(map, parent[current])
                    and dist < nearest_distance
                ):
                    nearest_neighbor = neighbor
                    nearest_distance = dist
                    nearest_neighbor_group = neighbor_group

        if nearest_neighbor is not None:
            path.append(nearest_neighbor)
            route += trace[:-1]
            total_cost += dist
            visited.add(nearest_neighbor)
            i = orig_neighbors.index(nearest_neighbor_group)
            parent[nearest_neighbor] = all_nodes[i+1]
            all_neighbors.remove(nearest_neighbor_group)
        else:
            # No unvisited neighbors found, the graph might be disconnected
            break

    # Add the start node to complete the cycle
    route += graph[(start, path[-1])][1][::-1]
    total_cost += graph[(start, path[-1])][0]

    path.append(start)
    print(path)
    return total_cost, route

def get_instructions(route: list, prod_db:dict, item_ids: list):
    """
    get instructions of a given route
    """

    instruction_str = ""
    all_neighbors = {}
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

    # if there are only one node in the route
    if len(route) == 1:
        instruction_str += "You can pick up the product at current position!\n"
        return

    start, next_pos = route[0], route[1]
    instruction = get_step_instruction(start, next_pos)
    dis = 1

    for idx in range(1, len(route) - 1):
        pos, next_pos = route[idx], route[idx + 1]
        for item in items:
            if next_pos in item.neighbors():
                instruction_str += f"Pick up the product!\n"
                items.remove(item)
                break

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
    instruction_str += "Return to the start position!\n"

    return instruction_str
