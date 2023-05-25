import matplotlib.pyplot as plt

# Define the nodes and their coordinates
nodes = {"A": (4, 5), "B": (6, 3), "C": (2, 7), "D": (8, 2), "E": (10, 4)}

# Define the access point directions
access_points = {"n": (0, 1), "s": (0, -1), "e": (1, 0), "w": (-1, 0)}

# Create a dictionary to store the distances between access points
access_point_distances = {}

# Create a dictionary to store the access points of each node
node_access_points = {}

# Initialize access point distances and node access points
for node, (x, y) in nodes.items():
    node_access_points[node] = {}
    for ap_direction, (dx, dy) in access_points.items():
        ap_x = x + dx
        ap_y = y + dy
        node_access_points[node][ap_direction] = (ap_x, ap_y)

# Calculate distances between access points of different nodes
for node1, aps1 in node_access_points.items():
    access_point_distances[node1] = {}
    for node2, aps2 in node_access_points.items():
        if node1 != node2:
            access_point_distances[node1][node2] = {}
            for ap1_direction, ap1_coords in aps1.items():
                shortest_distance = float("inf")
                for ap2_direction, ap2_coords in aps2.items():
                    dx = ap2_coords[0] - ap1_coords[0]
                    dy = ap2_coords[1] - ap1_coords[1]
                    distance = abs(dx) + abs(dy)
                    if distance < shortest_distance:
                        shortest_distance = distance
                access_point_distances[node1][node2][ap1_direction] = shortest_distance

# Create a new figure and axis
fig, ax = plt.subplots()

# Draw the nodes and their labels
for node, (x, y) in nodes.items():
    ax.scatter(x, y, color="lightblue", s=500)
    ax.annotate(
        node,
        (x, y),
        textcoords="offset points",
        xytext=(0, 0),
        ha="center",
        va="center",
    )

    distances_text = ""
    for other_node, ap_distances in access_point_distances[node].items():
        shortest_distance = float("inf")
        for ap1_direction, distance in ap_distances.items():
            if distance < shortest_distance:
                shortest_distance = distance
        distances_text += f"{other_node}: {shortest_distance}\n"

    ax.annotate(
        distances_text,
        (x, y),
        textcoords="offset points",
        xytext=(30, -10),
        ha="left",
        fontsize=8,
    )

# Set axis limits and labels
ax.set_xlim(0, 12)
ax.set_ylim(0, 8)
ax.set_xticks([])
ax.set_yticks([])

# Set the title and display the graph
ax.set_title("Shortest Distances Between Node Access Points")
plt.show()
