import matplotlib.pyplot as plt

# Define the nodes and their coordinates
nodes = {"A": (4, 5), "B": (6, 3), "C": (2, 7), "D": (8, 2), "E": (10, 4)}

# Define the access point directions
access_points = {"n": (0, 1), "s": (0, -1), "e": (1, 0), "w": (-1, 0)}

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

    # Draw the access points as smaller nodes and display the texts beside them
    for ap_direction, (dx, dy) in access_points.items():
        ap_x = x + dx
        ap_y = y + dy
        ap_text = f"{node}-{ap_direction}"
        ax.scatter(ap_x, ap_y, color="white", edgecolor="black", s=200)
        ax.annotate(
            ap_text,
            (ap_x, ap_y),
            textcoords="offset points",
            xytext=(0, 0),
            ha="center",
            va="center",
        )

        # Calculate and display distances between each node's access point to every other node's access point
        distances_text = ""
        for other_node, (other_x, other_y) in nodes.items():
            if node != other_node:
                distances_text += f"{other_node}:\n"
                for other_ap_direction, (other_dx, other_dy) in access_points.items():
                    other_ap_x = other_x + other_dx
                    other_ap_y = other_y + other_dy
                    manhattan_distance = abs(ap_x - other_ap_x) + abs(ap_y - other_ap_y)
                    distances_text += f"  {other_ap_direction}: {manhattan_distance}\n"

        ax.annotate(
            distances_text,
            (ap_x, ap_y),
            textcoords="offset points",
            xytext=(20, 0),
            ha="left",
            fontsize=8,
        )

# Set axis limits and labels
ax.set_xlim(0, 12)
ax.set_ylim(0, 8)
ax.set_xticks([])
ax.set_yticks([])

# Set the title and display the graph
ax.set_title("Distances between Node Access Points")
plt.show()
