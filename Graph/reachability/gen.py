import os
import networkx as nx
from networkx import Graph
import random

import sys

# Get the root directory path of the project
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)
from utils.gen import generate_graph


def generate_graphs(node_count_range, total_graphs, output_dir):
    """
    Generate 100 graphs using the generate_graph function.
    Each graph consists of num_components connected components.
    A query (u, v) is added at the end of each graph.
    - For the first 50 graphs, (u, v) are connected.
    - For the last 50 graphs, (u, v) are not connected.
    """
    half = total_graphs // 2  # The first half of the graphs have (u, v) connected, the second half does not.
    graphs = []

    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for i in range(total_graphs):
        num_nodes = random.randint(*node_count_range)  # Randomly generate the number of nodes
        # Randomly decide the number of connected components (ensuring there are at least 2 components in disconnected graphs)
        num_components = random.randint(2 - (i < half), min(max(2, num_nodes // 3), 4))

        if num_components == 1:
            edges = generate_graph("connected", num_nodes)
        else:
            edges = generate_graph("disconnected", num_nodes, num_components)

        # Convert to a NetworkX graph
        G = Graph()
        G.add_edges_from(edges)

        # Get connected components using NetworkX's connected_components
        components = [list(comp) for comp in nx.connected_components(G)]

        # Choose query nodes (u, v)
        if i < half:
            # For connected graphs, choose a pair (u, v) from the same component
            component = random.choice(components)
            u, v = random.sample(component, 2)
        else:
            # For disconnected graphs, choose a pair (u, v) from different components
            comp1, comp2 = random.sample(components, 2)
            u = random.choice(comp1)
            v = random.choice(comp2)

        graphs.append((G, u, v))

    # Save all graphs to files
    for idx, (G, u, v) in enumerate(graphs):
        with open(f"{output_dir}/graph{idx}.txt", "w") as f:
            f.write(f"{len(G.nodes)} {len(G.edges)}\n")  # Write the number of nodes and edges
            for a, b in G.edges:
                f.write(f"{a} {b}\n")  # Write each edge
            f.write(f"{u} {v}\n")  # Write the query pair (u, v)

    print(f"Generated {total_graphs} graphs and saved them to the '{output_dir}' directory.")


# Example usage
node_count_range = (31, 40)  # Range of node counts
total_graphs = 100  # Total number of graphs to generate
output_dir = "graph/hard/standard"  # Directory to save the graph files

generate_graphs(node_count_range, total_graphs, output_dir)