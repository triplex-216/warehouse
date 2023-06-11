from itertools import permutations
from random import sample, randint, choice
from lib.route import Node, AccessPoint, SingleNode


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
    size = len(individual)
    copy = individual[:]
    # Generate 2 indexes and swap the elements
    i, j = sample(range(size), k=2)
    copy[i], copy[j] = copy[j], copy[i]

    return copy


def crossover(
    a: list[AccessPoint],
    b: list[AccessPoint],
) -> list[AccessPoint]:

    size = len(a)
    crossover_point = randint(0, size - 1)
    a_parent = [ap.parent for ap in a[: crossover_point]]
    b_parent = [ap.parent for ap in b[: crossover_point]]
    child_a = a[: crossover_point] + [ap for ap in b if ap.parent not in a_parent]
    child_b = b[: crossover_point] + [ap for ap in a if ap.parent not in b_parent]

    return child_a, child_b


def genetic(
    item_nodes, start_node, end_node, rounds=0
) -> tuple[list[list[AccessPoint]], list[float]]:
    def show_individual(individual, start_node, end_node):
        individual_path = start_node.aps + individual + end_node.aps
        return f"{[n.coord for n in individual_path]}"

    # all_nodes = [start_node] + item_nodes + [end_node]

    size = int(len(item_nodes) * (len(item_nodes) - 1) / 2)

    if rounds == 0:
        rounds = min(int((len(item_nodes) ** 2) / 2), 30)

    population = generate_population(item_nodes, size=size)

    print("Generated initial population by randomly sampling from permutations: ")
    for idx, individual in enumerate(population):
        print(
            f"{idx + 1}: {show_individual(individual, start_node, end_node)}, fitness={gt_cost(individual, start_node, end_node)}"
        )

    for r in range(rounds):
        print(f"\nRound {r + 1}/{rounds}")
        # Cross over best 2
        # print("\nCross over stage: ")
        for _ in range(int(size / 2)):
            [a, b] = sample(
                sorted(population, key=lambda i: gt_cost(i, start_node, end_node)), k=2
            )
            child_a, child_b = crossover(a, b)

            population.extend([child_a, child_b])

        # Mutate best half to yield half children
        # print("\nMutation stage: ")
        population = sorted(population, key=lambda i: gt_cost(i, start_node, end_node))
        for _ in range(int(size / 2)):
            parent = population[_]
            child = mutate(parent)
            # print(f"{show_individual(child, start_node, end_node)} <== {show_individual(parent, start_node, end_node)}")
            population.append(child)

        # Sort population by gt_cost and keep the best n individual
        population = sorted(population, key=lambda i: gt_cost(i, start_node, end_node))[
            :size
        ]

        # print("\nRound finished; showing several best individuals from population: ")
        # for idx, individual in enumerate(population):
        #     if idx > 9:
        #         break
        #     print(
        #         f"{idx + 1}: {show_individual(individual, start_node, end_node)}, fitness={gt_cost(individual, start_node, end_node)}"
        #     )

        # print(
        #     f"Best result: {show_individual(population[0], start_node, end_node)}, fitness={gt_cost(population[0], start_node, end_node)}, Route Cost={gt_cost(population[0], start_node, end_node)}"
        # )

    return (
        gt_cost(population[0], start_node, end_node),
        start_node.aps + population[0] + end_node.aps,
    )
