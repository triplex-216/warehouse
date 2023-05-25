import matplotlib.pyplot as plt
from lib.core import *
from lib.route import *
from lib.tui import *
DATASET = "data/qvBox-warehouse-data-s23-v01.txt"

def Merge(dict1, dict2): 
    res = {**dict1, **dict2} 
    return res 

def get_distance(map, start, end):
    dir = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    row, col = len(map), len(map[0])
    dis = {}

    def get_neighbors(node):
        neighbors = []
        for x, y in dir:
            neighbor = (node[0] + x, node[1] + y)
            if (
                neighbor[0] in range(row)
                and neighbor[1] in range(col)
                and map[neighbor[0]][neighbor[1]] == 0
            ):
                neighbors.append(neighbor)
        return neighbors

    # If find path to adjacent grids, consider all the end grid's neighbors
    # Else only consider the end grid itself.
    if end == (0,0):
        end_positions = [end]
    else:
        end_positions = get_neighbors(end)
    
    if start == (0,0):
        start_positions = [start]
    else:
        start_positions = get_neighbors(start)

    for start_point in start_positions:
        # Initialize the distance dictionary with the starting node and a cost of 0
        distance = {start_point: 0}
        # Initialize the priority queue with the starting node and its cost
        visited_set = [(0, start_point)]
        while visited_set and end_positions:
            # Get the node with the lowest cost from the priority queue
            current_node = heapq.heappop(visited_set)[1]

            if current_node in end_positions:
                end_positions.remove(current_node)
                dis[(start_point,current_node)] = distance[current_node]

            # Check each neighbor of the current node
            for neighbor in get_neighbors(current_node):
                # Calculate the tentative cost to reach the neighbor
                tentative_dis = distance[current_node] + 1
                # If the neighbor is not in the open set or the tentative cost is less than the existing cost, add it to the open set
                if tentative_dis < distance.get(neighbor, float("inf")):
                    distance[neighbor] = tentative_dis
                    heapq.heappush(visited_set, (tentative_dis, neighbor))

    return dis
# Node coordinates
# nodes = {
#     'A': (2, 5),
#     'B': (4, 8),
#     'C': (6, 3),
#     'D': (9, 6),
#     'E': (12, 4)
# }
map_data, prod_db = read_inventory_data(DATASET)
rows, cols = len(map_data), len(map_data[0])
item_count = input_data_as_list("How many items would you like to fetch? ", "d", 1)[
    0
]
item_ids = input_data_as_list(
    "Please input IDs of the items you wish to add to list", "d", item_count
)
nodes = [(0,0)] + get_item_locations(product_db=prod_db, id_list=item_ids)
#calculate distances
distance = {}
for i in range(len(nodes)):
    for j in range(i+1,len(nodes)):
        dis = get_distance(map_data, nodes[i], nodes[j])
        distance = Merge(dis, distance) 

print(distance)# Edge connections and distances
# edges = {
#     ('A', 'B'): 4,
#     ('A', 'C'): 6,
#     ('B', 'C'): 5,
#     ('B', 'D'): 7,
#     ('C', 'D'): 3,
#     ('C', 'E'): 8,
#     ('D', 'E'): 5
# }

# Create a figure and axis
fig, ax = plt.subplots()

# Draw nodes
for node, coordinates in nodes.items():
    ax.plot(coordinates[0], coordinates[1], 'ro')  # 'ro' represents red circles
    ax.annotate(node, coordinates, textcoords="offset points", xytext=(0,10), ha='center')

# Draw edges
for edge, distance in edges.items():
    node1, node2 = edge
    x_coords = [nodes[node1][0], nodes[node2][0]]
    y_coords = [nodes[node1][1], nodes[node2][1]]
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
