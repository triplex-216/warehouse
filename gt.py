from itertools import permutations
from random import sample, randint, choice
from lib.route import cost, Node, AccessPoint


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


def fitness(individual: list[AccessPoint]) -> float:
    cost = 0
    size = len(individual)
    for i in range(size):
        curr, nxt = individual[i], individual[(i + 1) % size]
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


def crossover(a: list[AccessPoint], b: list[AccessPoint]) -> list[AccessPoint]:
    a_parents = {node.parent for node in a}
    b_parents = {node.parent for node in b}
    all_parents = a_parents.union(b_parents)
    size = len(a)  # Assume equal length

    while True:
        idx = randint(0, size - 1)
        child_a, child_b = (a[:idx] + b[idx:]), (b[:idx] + a[idx:])

        # Keep the better child
        better_child = max([child_a, child_b], key=fitness)
        better_child_parents = {node.parent for node in better_child}
        
        if better_child_parents == all_parents:
            break

    return better_child


def genetic(item_nodes, rounds=5) -> tuple[list[list[AccessPoint]], list[float]]:
    def show_individual(individual):
        return f"{[n.coord for n in individual]}"

    size = int(len(item_nodes) * (len(item_nodes) - 1) / 2)

    population = generate_population(item_nodes, size=size)

    print("Generated initial population by randomly sampling from permutations: ")
    for idx, individual in enumerate(population):
        print(
            f"{idx + 1}: {show_individual(individual)}, Fitness={fitness(individual)}"
        )

    n = size
    for r in range(rounds):
        print(f"\nRound {r + 1}/{rounds}")
        # Cross over best 2 
        print("\nCross over stage: ")
        for _ in range(int(n/2)):
            a, b = sorted(population, key=lambda i: fitness(i))[:2]
            child = crossover(a, b)
            print(
                f"{show_individual(child)} <== {show_individual(a)}, {show_individual(b)}"
            )
            population.append(child)

        # Mutate best half to yield half children
        print("\nMutation stage: ")
        population = sorted(population, key=lambda i: fitness(i))
        for _ in range(int(n/2)):
            parent = population[_]
            child = mutate(parent)
            print(f"{show_individual(child)} <== {show_individual(parent)}")
            population.append(child)

        # Sort population by fitness and keep the best n individual
        population = sorted(population, key=lambda i: fitness(i))[:n]

        print("\nRound finished; showing best 10 individuals from population: ")
        for idx, individual in enumerate(population):
            if idx > 9:
                break
            print(
                f"{idx + 1}: {show_individual(individual)}, Fitness={fitness(individual)}"
            )

        print(
            f"Best result: {show_individual(population[0])}, Fitness={fitness(population[0])}, Route Cost={fitness(population[0])}"
        )

    return population, list(map(fitness, population))
