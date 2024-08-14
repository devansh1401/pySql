import networkx as nx
import matplotlib.pyplot as plt

# Create a graph
G = nx.Graph()

# Add nodes
G.add_nodes_from([1, 2, 3, 4, 5])

# Add edges
G.add_edges_from([(1, 2), (1, 3), (2, 4), (3, 5), (4, 5)])

# Draw the graph
nx.draw(G, with_labels=True, node_color='lightblue', node_size=500, font_size=16)

# Save the graph as an image
plt.savefig('graph.png')

# Display the graph (if you're in an interactive environment)
plt.show()