import heapq
from .core import Node, AccessPoint, PriorityQueue

def greedy(
    nodes: list[Node], start_ap: AccessPoint, end_ap: AccessPoint, init_ap: AccessPoint
):
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
    all_path = PriorityQueue()
    for node in nodes:
        for ap in node.aps:
            cost, path = greedy(nodes, start_ap, end_ap, ap)
            all_path.enqueue(path, cost)

    bestcost, bestpath = all_path.dequeue()
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