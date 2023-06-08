from itertools import permutations
from random import sample, randint, choice
from lib.route import Node, AccessPoint, SingleNode


def generate_population(
    item_nodes: list[Node], size: int = 10
) -> list[list[AccessPoint]]:
    population = None
    for i in range(size):
        # Get a random access points of each node
        aps = [choice(n.aps) for n in item_nodes]
        ap_coordinates = [ap.coord for ap in aps]
        if population == None:
            population = sample(list(permutations(aps)), k=1)
        else:
            population += sample(list(permutations(aps)), k=1)
    population = [list(p) for p in population]  # Convert from tuple to list
    return population


def gt_cost(individual: list[AccessPoint], start_node: SingleNode, end_node: SingleNode) -> float:
    # Add start and end for individual path
    individual_path = start_node.aps + individual + end_node.aps

    cost = 0
    size = len(individual_path)
    for i in range(size):
        curr, nxt = individual_path[i], individual_path[(i + 1) % size]
        if curr == nxt:
            return float("inf")
        # Avoid access same node's different ap when doing crossover
        if curr.parent.coord == nxt.parent.coord:
            return float("inf")
        cost += curr.dv[nxt][0]
    return cost


def mutate(individual: list[AccessPoint]) -> list[AccessPoint]:
    size = len(individual)
    copy = individual[:]
    # Generate 2 indexes and swap the elements
    i, j = sample(range(size), k=2)
    copy[i], copy[j] = copy[j], copy[i]

    return copy


def crossover(a: list[AccessPoint], b: list[AccessPoint], start_node: SingleNode, end_node: SingleNode) -> list[AccessPoint]:
    a_parents = {node.parent for node in a}
    b_parents = {node.parent for node in b}
    all_parents = a_parents.union(b_parents)
    size = len(a)  # Assume equal length

    while True:
        idx = randint(0, size - 1)
        child_a, child_b = (a[:idx] + b[idx:]), (b[:idx] + a[idx:])

        # Keep the better child
        a_fit = gt_cost(child_a, start_node, end_node)
        b_fit = gt_cost(child_b, start_node, end_node)
        if a_fit > b_fit:
            better_child = child_b
        else:
            better_child = child_a
        better_child_parents = {node.parent for node in better_child}
        
        if better_child_parents == all_parents:
            break

    return better_child


def genetic(item_nodes, start_node, end_node, rounds=10) -> tuple[list[list[AccessPoint]], list[float]]:
    def show_individual(individual, start_node, end_node):
        individual_path = start_node.aps + individual + end_node.aps
        return f"{[n.coord for n in individual_path]}"

    size = int(len(item_nodes) * (len(item_nodes) - 1) / 2)

    population = generate_population(item_nodes, size=size)

    print("Generated initial population by randomly sampling from permutations: ")
    for idx, individual in enumerate(population):
        print(
            f"{idx + 1}: {show_individual(individual, start_node, end_node)}, fitness={gt_cost(individual, start_node, end_node)}"
        )

    n = size
    for r in range(rounds):
        
        # print(f"\nRound {r + 1}/{rounds}")
        # Cross over best 2 
        # print("\nCross over stage: ")
        for _ in range(int(n/2)):
            a, b = sorted(population, key=lambda i: gt_cost(i, start_node, end_node))[:2]
            child = crossover(a, b, start_node, end_node)
            # print(
            #    f"{show_individual(child, start_node, end_node)} <== {show_individual(a, start_node, end_node)}, {show_individual(b, start_node, end_node)}"
            # )
            population.append(child)

        # Mutate best half to yield half children
        # print("\nMutation stage: ")
        population = sorted(population, key=lambda i: gt_cost(i, start_node, end_node))
        for _ in range(int(n/2)):
            parent = population[_]
            child = mutate(parent)
            # print(f"{show_individual(child, start_node, end_node)} <== {show_individual(parent, start_node, end_node)}")
            population.append(child)

        # Sort population by gt_cost and keep the best n individual
        population = sorted(population, key=lambda i: gt_cost(i, start_node, end_node))[:n]

        print("\nRound finished; showing several best individuals from population: ")
        for idx, individual in enumerate(population):
            if idx > 9:
                break
            print(
                f"{idx + 1}: {show_individual(individual, start_node, end_node)}, fitness={gt_cost(individual, start_node, end_node)}"
            )

        print(
            f"Best result: {show_individual(population[0], start_node, end_node)}, fitness={gt_cost(population[0], start_node, end_node)}, Route Cost={gt_cost(population[0], start_node, end_node)}"
        )

    return start_node.aps + population[0] + end_node.aps, gt_cost(population[0], start_node, end_node)
