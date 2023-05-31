import heapq
from .core import get_item, get_item_locations
from .branch_and_bound import branch_and_bound
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
        positions1 = get_neighbors(map, node1)
    
    if node2 == start or node2 == end:
        positions2 = [node2]
    else:
        positions2 = get_neighbors(map, node2)

    for p1 in positions1:
        for p2 in positions2:
            dis[(p1, p2)] = cost(map, p1, p2)
            dis[(p2, p1)] = cost(map, p2, p1)

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

        for item in items:
            for neighbor in item.neighbors():
                dist, trace = graph[(current, neighbor)]

                if neighbor not in route and dist < nearest_distance:
                    nearest_neighbor = neighbor
                    nearest_distance = dist
                    nearest_trace = trace

        if nearest_neighbor is not None:
            route += nearest_trace[1:]
            total_cost += nearest_distance
            #remove visited items
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

def nearest_neighbor(graph, items, start=(0, 0), end=(0,0)):

    pass
def default(graph, items, start=(0, 0), end=(0,0)):
    route = [start]
    total_cost = 0
    visited = {start}

    for item in items:
        for neighbor in item.neighbors():
            if neighbor in route:
                visited.add(item)
                break
        if item not in visited:
            cost, trace = graph[(route[-1], item.neighbors()[0])]
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
            if pos in item.neighbors():
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
    all_nodes = [start] + get_item_locations(prod_db, item_ids) + [end]
    graph = get_graph(map, all_nodes)
    items = get_item(prod_db, item_ids)
    
    if algorithm == "b":  # branch and bound
        total_cost, route = branch_and_bound(map=map, prod_db=prod_db, item_ids=item_ids, start=start)
    elif algorithm == "g":  # greedy
        total_cost, route = greedy(
            graph=graph, items=items, start=start
        )
    elif algorithm == "f":  # fallback
        total_cost, route = default(
            graph=graph, items=items, start=start
        )
    
    return total_cost, route
