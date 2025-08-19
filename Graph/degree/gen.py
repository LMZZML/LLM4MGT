import networkx as nx
import random
from networkx import Graph
import os

import sys
# Get the project root directory path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)
from utils.gen import generate_graph


def generate_graphs(node_count_range, total_graphs, output_dir):
    """
    Generate graphs using the generate_graph function.
    After generating each graph, randomly select a node as the query point.
    """
    graphs = []

    # Create the output directory (if it doesn't exist)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for i in range(total_graphs):
        num_nodes = random.randint(*node_count_range)  # Randomly generate the number of nodes
        num_components = random.randint(1, min(max(2, num_nodes // 3), 4))  # Number of connected components
        if num_components == 1:
            edges = generate_graph("connected", num_nodes)
        else:
            edges = generate_graph("disconnected", num_nodes, num_components)

        # Convert to a NetworkX graph object
        G = Graph()
        G.add_edges_from(edges)

        # Randomly select a node as the query node
        random_node = random.randint(0, num_nodes - 1)

        graphs.append((G, random_node))

    # Save all graphs to files
    for idx, (G, random_node) in enumerate(graphs):
        with open(f"{output_dir}/graph{idx}.txt", "w") as f:
            f.write(f"{len(G.nodes)} {len(G.edges)}\n")  # Write the number of nodes and edges
            for a, b in G.edges:
                f.write(f"{a} {b}\n")  # Write each edge
            f.write(f"{random_node}\n")  # Write the random node

    print(f"Generated {total_graphs} graphs and saved to the '{output_dir}' directory.")


# Example usage
node_count_range = (31, 40)  # Range of node counts
total_graphs = 100  # Total number of graphs to generate
output_dir = "graph/hard/standard"  # Directory to save the graph files

generate_graphs(node_count_range, total_graphs, output_dir)