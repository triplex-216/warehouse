from itertools import permutations
from random import sample, randint
from .route import cost, SingleNode, AccessPoint


def generate_population(
    item_nodes: list[SingleNode], size: int = 10
) -> list[list[AccessPoint]]:
    # Get actual access points of each single access node
    aps = [next(iter((n.neighbors.values()))) for n in item_nodes]
    ap_coordinates = [ap.coord for ap in aps]

    population = sample(list(permutations(aps)), k=size)
    population = [list(p) for p in population]  # Convert from tuple to list
    return population


def fitness(individual: list[AccessPoint]) -> float:
    cost = 0
    size = len(individual)
    for i in range(size):
        curr, nxt = individual[i], individual[(i + 1) % size]
        if curr == nxt:
            return float("inf")
        cost += curr.dv[nxt][0]
    return 1.0 / cost


def mutate(individual: list[AccessPoint]) -> list[AccessPoint]:
    size = len(individual)
    copy = individual[:]
    # Generate 2 indexes and swap the elements
    i, j = sample(range(size), k=2)
    copy[i], copy[j] = copy[j], copy[i]

    return copy


def crossover(a: list[AccessPoint], b: list[AccessPoint]) -> list[AccessPoint]:
    all_elements = set(a).union(set(b))
    size = len(a)  # Assume equal length

    while True:
        idx = randint(0, size - 1)
        child_a, child_b = (a[:idx] + b[idx:]), (b[:idx] + a[idx:])

        # Keep the better child
        better_child = max([child_a, child_b], key=fitness)
        if set(better_child) == all_elements:
            break

    return better_child


def genetic(item_nodes, rounds=3) -> tuple[list[list[AccessPoint]], list[float]]:
    def show_individual(individual):
        return f"{[n.coord for n in individual]}"

    population = generate_population(item_nodes, size=10)

    print("Generated initial population by randomly sampling from permutations: ")
    for idx, individual in enumerate(population):
        print(
            f"{idx}: {show_individual(individual)}, Fitness={fitness(individual):.4f}"
        )

    n = 10
    for r in range(rounds):
        print(f"\nRound {r + 1}/{rounds}")
        # Cross over best 2 for 5 times
        print("\nCross over stage: ")
        for _ in range(5):
            a, b = sorted(population, key=lambda i: fitness(i), reverse=True)[:2]
            child = crossover(a, b)
            print(
                f"{show_individual(child)} <== {show_individual(a)}, {show_individual(b)}"
            )
            population.append(child)

        # Mutate best 5 to yield 5 children
        print("\nMutation stage: ")
        population = sorted(population, key=lambda i: fitness(i), reverse=True)
        for _ in range(5):
            parent = population[_]
            child = mutate(parent)
            print(f"{show_individual(child)} <== {show_individual(parent)}")
            population.append(child)

        # Sort population by fitness and keep the best n individual
        population = sorted(population, key=lambda i: fitness(i), reverse=True)[:n]

        print("\nRound finished; showing best 10 individuals from population: ")
        for idx, individual in enumerate(population):
            print(
                f"{idx}: {show_individual(individual)}, Fitness={fitness(individual):.4f}"
            )

        print(
            f"Best result: {show_individual(individual)}, Fitness={fitness(individual):.4f}, Route Cost={1/fitness(individual)}"
        )

    return population, list(map(fitness, population))
