import random
import matplotlib.pyplot as plt
import heapq
from itertools import combinations
from lib.core import *
from lib.route import *

DATASET = "data/qvBox-warehouse-data-s23-v01.txt"
POPULATION_SIZE = 10
NUM_GENERATION = 3

def single_access(items, start=(0,0)):
    access_points = [start]
    # choose the first neighbor of item as its single access point
    for item in items:
        for neighbor in item.neighbors():
            if neighbor:
                access_points.append(neighbor)
                break
    return access_points

# generate graph
def generate_graph(access_points):
    graph = {}
    for (node1, node2) in combinations(access_points, 2):
        graph[(node1, node2)] = cost(map_data, node1, node2)[0]
        graph[(node2, node1)] = cost(map_data, node1, node2)[0]
    
    return graph

def draw_graph(access_points, graph):
    # Create a figure and axis
    fig, ax = plt.subplots()

    # Draw nodes
    for node in access_points:
        ax.plot(node[0], node[1], 'ro')  # 'ro' represents red circles
        ax.annotate(node, node, textcoords="offset points", xytext=(0,10), ha='center')

    # Draw edges
    for edge, distance in graph.items():
        node1, node2 = edge
        x_coords = [node1[0], node2[0]]
        y_coords = [node1[1], node2[1]]
        ax.plot(x_coords, y_coords, 'b-')  # 'b-' represents blue lines
        mid_x = sum(x_coords) / 2
        mid_y = sum(y_coords) / 2
        ax.annotate(str(distance), (mid_x, mid_y), ha='center')

    # Set axis labels and title
    ax.set_xlabel('X-axis')
    ax.set_ylabel('Y-axis')
    ax.set_title('Map between Nodes')

    # Display the plot
    plt.show()

def init_population(size, nodes):
    # choose routes randomly to init population
    population = []
    for _ in range(size):
        individual = random.sample(nodes, len(nodes))  # Generate a random permutation of nodes
        population.append(individual)
    return population

# Calculate the fitness(total distance) of route
def calculate_fitness(graph, individual):
    total_distance = 0
    for i in range(len(individual)):
        node = individual[i]
        next_node = individual[(i+1) % len(individual)] # Wrap around to the first node
        total_distance += graph[(node, next_node)]
    
    return total_distance

# crossover
def crossover(parent1, parent2):
    # Randomly select a crossover point
    crossover_point = random.randint(1, len(parent1) - 1)
    # Perform crossover by swapping genetic material
    child1 = parent1[:crossover_point] + [node for node in parent2 if node not in parent1[:crossover_point]]
    child2 = parent2[:crossover_point] + [node for node in parent1 if node not in parent2[:crossover_point]]

    return child1, child2

# mutation
def mutation(individual):
    mutated_individual = individual.copy()
    swap_indices = random.sample(range(len(individual)), 2)
    # swap the oder of randomly picked 2 nodes in the route
    mutated_individual[swap_indices[0]], mutated_individual[swap_indices[1]] = \
        mutated_individual[swap_indices[1]], mutated_individual[swap_indices[0]]
    return mutated_individual

def genetic_algorithm(access_points, graph):
    population = init_population(size=POPULATION_SIZE, nodes=access_points)
    print("Initial Population")
    print(*population, sep="\n")
    print()
    best_fitness = float('inf')
    best_individual = None

    for generation in range(NUM_GENERATION):
        fitness_scores = []
        for individual in population:
            fitness = calculate_fitness(graph, individual)
            heapq.heappush(fitness_scores,(fitness, individual))

        print("Current Population and Fitness")
        for item in fitness_scores:
            print(f"individual: {item[1]}  fitness: {item[0]}")
        print()

        # Find the best individual in the current generation
        min_fitness = fitness_scores[0][0]
        if min_fitness < best_fitness:
            best_fitness = min_fitness
            best_individual = fitness_scores[0][1]

        children = []
        # increase the population through crossover and mutation, extend 10 individuals
        while len(children) < POPULATION_SIZE:
            parents = heapq.nsmallest(2, fitness_scores)
            parent1, parent2 = parents[0][1], parents[1][1]

            child1 = random.choice(crossover(parent1, parent2))
            heapq.heappush(fitness_scores,(calculate_fitness(graph, child1), child1))

            child2 = mutation(parent1)
            heapq.heappush(fitness_scores,(calculate_fitness(graph, child2), child2))

            children.extend([child1, child2])

        print("Extended population and Fitness")
        for item in fitness_scores:
            print(f"individual: {item[1]}  fitness: {item[0]}") 
        print()
        # choose top 10 as next generation
        population = [individual[1] for individual in heapq.nsmallest(10, fitness_scores)]

    route = best_individual + [start]
    return route, best_fitness

def nearest_neighbor(access_points, graph):
    start = random.choice(access_points) # choose start node randomly
    route = [start]
    visited = {start}
    distance = 0
    # loop until all nodes are visited
    while len(visited) < len(access_points):
        curr = route[-1]
        nearest_dis = float("inf")
        nearest_node = None
        # find the nearest neighbor
        for node in access_points:
            if node not in visited and graph[(curr, node)] < nearest_dis:
                nearest_dis = graph[(curr, node)]
                nearest_node = node
        # add nearest neighbor to route
        visited.add(nearest_node)
        route.append(nearest_node)
        distance += nearest_dis
    # Back to start.
    distance += graph[(route[-1], start)]
    route.append(start)

    return route, distance


map_data, prod_db = read_inventory_data(DATASET)
id_list = id_list = [108335, 391825, 340367]
start = (0, 0)
items = get_item(prod_db, id_list)
print(get_item_locations(prod_db, id_list))
access_points = single_access(items, start)
graph = generate_graph(access_points)
draw_graph(access_points, graph)
route, distance = genetic_algorithm(access_points, graph)
print(route, distance)
route, distance = nearest_neighbor(access_points, graph)
print(route, distance)


