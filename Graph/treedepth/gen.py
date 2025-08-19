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
    Use the generate_graph function to generate edge-weighted trees.
    """
    # Create output directory if it does not exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for idx in range(total_graphs):
        num_nodes = random.randint(*node_count_range)  # Randomly generate the number of nodes

        # Call the generate_graph function to generate the tree
        edges = generate_graph("tree", num_nodes)

        # Save the graph to a file
        with open(f"{output_dir}/graph{idx}.txt", "w") as f:
            f.write(f"{num_nodes} {len(edges)}\n")  # Write the number of nodes and edges
            for a, b in edges:
                f.write(f"{a} {b}\n")  # Write the edges

    print(f"Generated {total_graphs} graphs and saved them to the '{output_dir}' directory.")


# Example usage
node_count_range = (31, 40)  # The range of node counts
total_graphs = 100  # Total number of graphs to generate
output_dir = "graph/hard/standard"  # Directory to save graph files

generate_graphs(node_count_range, total_graphs, output_dir)