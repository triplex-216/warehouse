# Resolves class type hinting itself, see https://stackoverflow.com/a/33533514
from __future__ import annotations

import heapq
from itertools import combinations, product
from .core import *


class AccessPoint:
    def __init__(self, coord: tuple[int, int], parent: Node) -> None:
        self.coord = coord
        self.parent = parent  # Pointer to parent node
        self.dv = dict()  # Initialize distance vector

    def add_path(
        self, destination: AccessPoint, distance: int, path: list[tuple[int, int]]
    ) -> None:
        """
        Add a path to the distance vector. The path goes from this AP
        to another AP with a tuple containing the path's distance and
        grid-by-grid path to take
        """
        self.dv[destination] = (distance, path)
        destination.dv[self] = (distance, path[::-1])

    def get_nearest_ap(self) -> tuple[int, list[tuple[int, int]]]:
        """
        Return the nearest AP stored in the current AP's distance vector
        """
        return min(self.dv.items(), key=lambda item: item[1][0])


class Node:
    """
    A Node describes an item in the warehouse. Aside from an ID, it has
    a coordinate and up to 4 APs (AccessPoint, defined in the AccessPoint class).

    Each Node instance is intended to be initialized with a map. The
    map binding should not be changed once created, as the underlying
    AccessPoints depend on the map.

    After creation of Nodes, the distance vectors in their APs are empty
    and do not store any distance information. generate_cost_graph()
    must be called to calculate and create that information, see its
    documentation for usage.
    """

    def __init__(self, id: int, coord: tuple[int, int], map) -> None:
        self.id, self.coord = id, coord

        # The product's neighbors; initialized with empty elements and will be updated later
        self._ap = {"n": None, "e": None, "s": None, "w": None}
        # Bind reference to the map from which this product instance was created
        self._map = map

        # Detect valid neighbors (access points)
        aps = get_aps(self._map, self.coord)
        # Assign each neighbor to a direction (n/s/e/w)
        for ap in aps:
            offset = (ap[0] - self.coord[0], ap[1] - self.coord[1])
            match offset:
                case (1, 0):
                    self._ap["n"] = AccessPoint(coord=ap, parent=self)
                case (0, 1):
                    self._ap["e"] = AccessPoint(coord=ap, parent=self)
                case (-1, 0):
                    self._ap["s"] = AccessPoint(coord=ap, parent=self)
                case (0, -1):
                    self._ap["w"] = AccessPoint(coord=ap, parent=self)

    @property
    def x(self) -> int:
        return self.coord[0]

    @property
    def y(self) -> int:
        return self.coord[1]

    @property
    def n(self) -> AccessPoint:
        return self._ap["n"]

    @property
    def e(self) -> AccessPoint:
        return self._ap["e"]

    @property
    def s(self) -> AccessPoint:
        return self._ap["s"]

    @property
    def w(self) -> AccessPoint:
        return self._ap["w"]

    @property
    def aps(self):
        return [v for v in self._ap.values() if v]

    @property
    def aps_as_list(self) -> list[AccessPoint]:
        """
        Return a list of neighbors containing empty directions,
        For example, "n" would be None if the north AP doesn't exist
        """
        return list(self._ap.values())


class SingleNode(Node):
    """
    Single Access Nodes that are on both "ends" of the nodes list, i.e.
    the starting or ending nodes. SingleNode have a item ID of 0 and a north
    AP that has the same coordinate as the SingleNode themselves, so that they
    can be treated like standard Nodes in algorithms.
    """

    def __init__(self, coord, map, access_self=True):
        super().__init__(-1, coord, map)  # Initialize APs like a normal Node

        if access_self:
            # If the node's grid itself can be accessed,
            # i.e. Start/End nodes where no AP is necessary
            self._ap["n"] = AccessPoint(coord=self.coord, parent=self)
            # Remove all APs except the north one, and set it to have the
            # same coordinate as the node
            for direction in ["e", "s", "w"]:
                self._ap[direction] = None
        else:
            # Keep the first available AP and drop others
            # Has a priority: N-E-S-W
            drop = True
            for direction in ["n", "e", "s", "w"]:
                if not drop:
                    self._ap[direction] = None
                if self._ap[direction]:
                    drop = False  # Drop APs on other directions


def prod_to_node(prod: Prod):
    return Node(prod.id, (prod.x, prod.y), prod._map)


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
        start_ap, end_ap = start_node.aps_as_list[0], end_node.aps_as_list[0]
        # Set distance[(node, start)] = inf to ensure no one can access start
        for node in nodes:
            if node != start_node:
                for ap in node.aps:
                    _, path = ap.dv[start_ap]
                    ap.dv[start_ap] = (float("inf"), path)
        # Set distance[(end, start)] = 0 to ensure end to start is connected
        end_ap.dv[start_ap] = (0, [None])

    print(f"edges={edges}")

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
    # Initialize the priority queue with the starting node and its cost
    open_set = [(0, start)]
    while open_set:
        # Get the node with the lowest cost from the priority queue
        current_node = heapq.heappop(open_set)[1]

        if current_node == end:
            while current_node in parent:
                route.append(current_node)
                current_node = parent[current_node]
            # append route with start node
            route.append(start)
            costs = len(route) - 1
            return (costs, route[::-1])

        # Check each neighbor of the current node
        for neighbor in get_aps(map, current_node):
            # Calculate the tentative cost to reach the neighbor
            tentative_dis = distance[current_node] + 1
            # If the neighbor is not in the open set or the tentative cost is less than the existing cost, add it to the open set
            if tentative_dis < distance.get(neighbor, float("inf")):
                distance[neighbor] = tentative_dis
                heapq.heappush(open_set, (tentative_dis, neighbor))
                parent[neighbor] = current_node

    print(f"Path from {start} to {end} not found, check if it is a shelf!")
    return None

def greedy(nodes: list[Node], start_ap: AccessPoint, end_ap: AccessPoint, init_ap: AccessPoint):
    """
    give a list of nodes, return the greedy route
    """
    # Init path, path is a list of ap
    if init_ap == start_ap:
        init_ap = end_ap
    path = [init_ap]
    # Init unvisited set
    unvisited = set(nodes)
    unvisited.remove(init_ap.parent)
    total_cost = 0

    while unvisited:
        current = path[-1]
        # end_node should always go to start_node
        if current == end_ap:
            path.append(start_ap)
            unvisited.remove(start_ap.parent)
            current = start_ap

        nearest_neighbor = None
        nearest_distance = float("inf")
        # search every access points of unvisited nodes
        for node in unvisited:
            ap: AccessPoint
            for ap in node.aps:
                if ap not in path:
                    dist, _trace = current.dv[ap]
                    if dist < nearest_distance:
                        nearest_neighbor = ap
                        nearest_distance = dist

        if nearest_neighbor:
            path.append(nearest_neighbor)
            total_cost += nearest_distance
            # remove visited
            unvisited.remove(nearest_neighbor.parent)
        else:
            # No unvisited neighbors found, the graph might be disconnected
            break

    # Add the back cost to complete the cycle
    dist, _trace = path[-1].dv[init_ap]
    total_cost += dist

    return total_cost, path

def nearest_neighbor(nodes: list[Node], start_ap: AccessPoint, end_ap: AccessPoint):
    all_path = []
    for node in nodes:
        for ap in node.aps:
            cost, path = greedy(nodes, start_ap, end_ap, ap)
            heapq.heappush(all_path, (cost, id(path), path))
    
    bestcost, _id, bestpath = heapq.heappop(all_path)
    return bestcost, bestpath

def default(nodes: list[Node], start_ap: AccessPoint, end_ap: AccessPoint):
    path = [start_ap]
    total_cost = 0
    curr = path[-1]

    for node in nodes[1:]:
        # access node though first not None ap
        next = node.aps[0]
        path.append(next)
        # record cost
        cost, trace = curr.dv[next]
        total_cost += cost
        # update curr
        curr = path[-1]

    # Add the back route to complete the cycle
    dist, _trace = path[-1].dv[start_ap]
    total_cost += dist

    return total_cost, path


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


def find_route(item_nodes: list[Node], start_node: SingleNode, end_node:SingleNode, algorithm="g"):
    # Calculate the graph(distance and route between all the accessible entries)
    start_ap, end_ap = start_node.aps_as_list[0], end_node.aps_as_list[0]
    nodes = [start_node] + item_nodes + [end_node]
    generate_cost_graph(nodes, start_node=start_node, end_node=end_node)

    if algorithm == "b":  # branch and bound
        print("WIP")
    elif algorithm == "g":  # greedy
        total_cost, path = greedy(nodes, start_ap, end_ap, init_ap=start_ap)
    elif algorithm == "n":
        total_cost, path = nearest_neighbor(nodes, start_ap, end_ap)
    elif algorithm == "f":  # fallback
        total_cost, path = default(nodes, start_ap, end_ap)
    
    instructions, route = path_instructions(path, start_ap, end_ap)
    return instructions, total_cost, route
