# Resolves class type hinting itself, see https://stackoverflow.com/a/33533514
from __future__ import annotations

import heapq
from collections import defaultdict
from itertools import combinations, product
from .core import *
from .bnb import *
from .genetic import *
from .nearest_neighbor import *
import multiprocessing
from time import sleep, time
from psutil import virtual_memory


def prod_to_node(prod_db, map_data, id_list):
    coord_to_ids = defaultdict(list)
    nodes = []
    for id in id_list:
        coord = prod_db[id]
        coord_to_ids[coord].append(id)
    for coord, id in coord_to_ids.items():
        nodes.append(Node(id, coord, map_data))
    return nodes


def generate_cost_graph(
    nodes: list[Node], start_node: SingleNode = None, end_node: SingleNode = None
) -> None:
    """
    Calculate and store costs between all possible AccessPoint pairs between
    all pairs of nodes from nodes_list.
    e.g. For each of the 16 pairs from the 8 APs: A{n,e,s,w} and B{n,e,s,w},
    calculate 16 distances and store in AccessPoints' distance vectors.

    start_node and end_node can be absent
    """
    # Clear all nodes' distance vectors to prevent accidentally accessing APs
    # from other orders and cause BnB to eat up RAM

    for n in nodes + [start_node] + [end_node]:
        n: Node | SingleNode
        ap: AccessPoint
        for ap in n.aps:
            ap.dv = dict()

    edges = 0
    for a, b in combinations(nodes, 2):
        ap_1: AccessPoint  # Type hints for IDE
        ap_2: AccessPoint
        for ap_1, ap_2 in product(a.aps, b.aps):
            # Skip if the AP pair has been calculated
            if ap_2 in ap_1.dv.keys():
                continue

            dist, route = cost(a._map, ap_1.coord, ap_2.coord)
            ap_1.add_path(destination=ap_2, distance=dist, path=route)
            edges += 1
            # print(f"{ap_1.coord} -> {ap_2.coord}: {dist}")

    if start_node and end_node:
        start_ap, end_ap = start_node.aps[0], end_node.aps[0]
        # Set distance[(node, start)] = inf to ensure no one can access start
        # Set distance[(end, node)] = inf to ensure end can not access any node exept start
        for node in nodes:
            if node != start_node:
                for ap in node.aps:
                    _, path = ap.dv[start_ap]
                    ap.dv[start_ap] = (float("inf"), path)
                    end_ap.dv[ap] = (float("inf"), path)
        # Set distance[(end, start)] = 0 to ensure end to start is connected
        end_ap.dv[start_ap] = (0, [None])
        start_ap.dv[end_ap] = (float("inf"), start_ap.dv[end_ap][1])


def cost(map, start, end) -> tuple[int, list[tuple[int, int]]]:
    """
    calculate distance and shortest route between two single entries
    """
    if not start or not end:
        return (float("inf"), [None])

    parent = {}
    route = []
    # Initialize the distance dictionary with the starting node and a cost of 0
    distance = {start: 0}
    turn_num = {start: 0}
    coming_dir = {start: None}
    # Initialize the priority queue with the starting node and its cost
    open_set = [(0, start)]
    while open_set:
        # Get the node with the lowest cost from the priority queue
        current_node = heapq.heappop(open_set)[-1]

        if current_node == end:
            while current_node in parent:
                route.append(current_node)
                current_node = parent[current_node]
            # append route with start node
            route.append(start)
            costs = len(route) - 1
            return (costs, route[::-1])

        # Check each neighbor of the current node
        for dir, neighbor in get_aps(map, current_node):
            # Calculate the tentative cost to reach the neighbor
            tentative_dis = distance[current_node] + 1
            # Calculate the number of turns to reach the neighbor
            if dir != coming_dir[current_node]:
                tentative_turns = turn_num[current_node] + 1
            else:
                tentative_turns = turn_num[current_node]
            # If the neighbor is not in the open set or the tentative cost is less than the existing cost, add it to the open set
            if tentative_dis < distance.get(neighbor, float("inf")):
                distance[neighbor] = tentative_dis
                turn_num[neighbor] = tentative_turns
                heapq.heappush(open_set, (tentative_dis, tentative_turns, neighbor))
                parent[neighbor] = current_node
                coming_dir[neighbor] = dir

    print(f"Path from {start} to {end} not found, check if it is a shelf!")
    return None


def path_instructions(
    path: list[AccessPoint], start_ap: AccessPoint, end_ap: AccessPoint
):
    """
    Transfer path to route with every coordinate of passed node contained
    """
    route = [start_ap.coord]
    instruction_str = ""
    # re-order the path to begin with start and terminate with end
    start_index = path.index(start_ap)
    path = path[start_index:] + path[:start_index]
    # print([ap.coord for ap in path])

    ap = path[0]
    for next in path[1:]:
        trace = ap.dv[next][1]
        route += trace[1:]
        instruction_str += get_step_instructions(trace)
        if next.parent.id == [-1]:
            instruction_str += "Return to the end position!\n"
        else:
            instruction_str += f"Pick up the product {next.parent.id}!\n"
        ap = next

    return instruction_str, route, len(route)-1


def get_step_instructions(trace: list[tuple]):
    """
    get instructions of a given route
    """

    def get_direction(position, next_position):
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

    instruction_str = ""
    # if there are only one node in the route
    if len(trace) == 1:
        return instruction_str

    start, next_pos = trace[0], trace[1]
    direction = get_direction(start, next_pos)
    step = 1

    for idx in range(1, len(trace) - 1):
        pos, next_pos = trace[idx], trace[idx + 1]
        new_direction = get_direction(pos, next_pos)
        # if two idr are the same
        if new_direction == direction:
            step += 1
        else:
            instruction_str += f"From {start} move {step} {'steps' if step > 1 else 'step'} {direction} to {pos}\n"
            direction = new_direction
            start = pos
            step = 1
    instruction_str += f"From {start}, move {step} {'steps' if step > 1 else 'step'} {direction} to {next_pos}\n"

    return instruction_str


def load_animation():
    while True:
        for c in "|/-\\":
            print(c, end="\r")
            sleep(0.1)


def _find_route(
    item_nodes: list[Node],
    start_node: SingleNode,
    end_node: SingleNode,
    algorithm="g",
    shared_list: list = [],
):
    """
    NOTE: Do not use this function directly, as it has the potential to use up all
    RAM when running BnB with an input that is large enough.
    Use find_route_with_timeout for RAM protection and timeout if wished.
    """

    # Calculate the graph(distance and route between all the accessible entries)
    start_ap, end_ap = start_node.aps_all[0], end_node.aps_all[0]
    nodes = [start_node] + item_nodes + [end_node]
    generate_cost_graph(nodes, start_node=start_node, end_node=end_node)

    if algorithm == "b":  # branch and bound
        _cost, path = branch_and_bound(nodes, start_ap, end_ap)
    elif algorithm == "g":  # greedy
        _cost, path = greedy(nodes, start_ap, end_ap, init_ap=start_ap)
    elif algorithm == "n":  # nearest neighbor
        _cost, path = nearest_neighbor(nodes, start_ap, end_ap)
    elif algorithm == "t":
        _cost, path = genetic(item_nodes, start_node, end_node)
    elif algorithm == "f":  # fallback
        _cost, path = default(nodes, start_ap, end_ap)

    instructions, route, total_cost = path_instructions(path, start_ap, end_ap)

    # Save return values as tuple into shared list for use in timeout monitor function
    shared_list.append((instructions, total_cost, route))

    return instructions, total_cost, route


def find_route(
    item_nodes: list[Node],
    start_node: SingleNode,
    end_node: SingleNode,
    algorithm: str,
    timeout: int,
):
    """
    Find route with the specified algorithm. The algorithm process will be killed
    after timeout.

    NOTE: Timeout = -1 disables timeout, and the algorithm will run indefinitely or
    until it uses too much RAM.
    """

    manager = multiprocessing.Manager()
    shared_list = manager.list()
    timeout_triggered = False  # Timeout indicator

    animation_process = multiprocessing.Process(
        target=load_animation,
    )
    algorithm_process = multiprocessing.Process(
        target=_find_route,
        args=(item_nodes, start_node, end_node, algorithm, shared_list),
    )

    animation_process.start()
    algorithm_process.start()

    if timeout == -1:  # No timeout
        timeout = float("inf")
    t_start = time()
    while True:
        sleep(0.1)
        if algorithm_process.is_alive():
            if time() - t_start > timeout:
                print(f"Algorithm timed out! Using fallback algorithm...")
                timeout_triggered = True
                break

            elif virtual_memory().percent > 80:
                print(f"Algorithm is using too much RAM! Using fallback algorithm...")
                timeout_triggered = True
                break

        else:
            # Algorithm finished successfully
            instructions, total_cost, route = shared_list[0]
            break

    if timeout_triggered:
        # If the algorithm is still alive after timeout, terminate the algorithm
        # and fallback to the default order
        algorithm_process.terminate()
        algorithm_process.join()

        instructions, total_cost, route = _find_route(
            item_nodes,
            start_node,
            end_node,
            "n",  # Use Nearest Neighbor algorithm as fallback (no timeout)
        )

    # Stop the loading animation
    animation_process.terminate()
    animation_process.join()

    return instructions, total_cost, route, timeout_triggered
