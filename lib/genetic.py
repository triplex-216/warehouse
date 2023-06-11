from itertools import permutations
from random import sample, randint, choice, random
from lib.route import Node, AccessPoint, SingleNode

MUTATION_RATE = 0.1


def generate_population(
    item_nodes: list[Node], size: int = 10
) -> list[list[AccessPoint]]:
    population = []
    for i in range(size):
        # Get a random access points of each node
        aps = [choice(n.aps) for n in item_nodes]
        population.append(sample(list(aps), k=len(aps)))

    return population


def gt_cost(
    individual: list[AccessPoint],
    start_node: SingleNode,
    end_node: SingleNode,
) -> float:
    # Add start and end for individual path
    full_path = start_node.aps + individual + end_node.aps

    cost = 0
    size = len(full_path)
    for i in range(size):
        curr, nxt = full_path[i], full_path[(i + 1) % size]
        cost += curr.dv[nxt][0]
    return cost


def mutate(individual: list[AccessPoint]) -> list[AccessPoint]:
    mutated_individual = individual.copy()
    if random() < MUTATION_RATE:
        size = len(individual)
        # Generate 2 indexes and swap the elements
        i, j = sample(range(size), k=2)
        mutated_individual[i], mutated_individual[j] = (
            mutated_individual[j],
            mutated_individual[i],
        )

    return mutated_individual


def crossover(
    a: list[AccessPoint],
    b: list[AccessPoint],
) -> list[AccessPoint]:
    size = len(a)
    crossover_point = randint(0, size - 1)
    a_parent = [ap.parent for ap in a[:crossover_point]]
    b_parent = [ap.parent for ap in b[:crossover_point]]
    child_a = a[:crossover_point] + [ap for ap in b if ap.parent not in a_parent]
    child_b = b[:crossover_point] + [ap for ap in a if ap.parent not in b_parent]

    return child_a, child_b


def genetic(
    item_nodes, start_node, end_node, rounds=0
) -> tuple[list[list[AccessPoint]], list[float]]:
    def show_individual(individual, start_node, end_node):
        individual_path = start_node.aps + individual + end_node.aps
        return f"{[n.coord for n in individual_path]}"

    # Keep population at a constant size
    size = int(len(item_nodes) * (len(item_nodes) - 1) / 2)

    if rounds == 0:
        rounds = max(int((len(item_nodes) ** 2) / 2), 100)

    population = generate_population(item_nodes, size=size)

    for r in range(rounds):
        for _ in range(int(size / 2)):
            population.sort(
                key=lambda individual: gt_cost(individual, start_node, end_node)
            )
            [parent_a, parent_b] = population[:2]
            child_a, child_b = crossover(parent_a, parent_b)
            mutated_child_a = mutate(child_a)
            mutated_child_b = mutate(child_b)
            population.extend([mutated_child_a, mutated_child_b])

        population.sort(
            key=lambda individual: gt_cost(individual, start_node, end_node)
        )
        population = population[:size]

    return (
        gt_cost(population[0], start_node, end_node),
        start_node.aps + population[0] + end_node.aps,
    )
