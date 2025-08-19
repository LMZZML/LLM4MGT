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
    Use the generate_graph function to generate unweighted trees.
    For each graph, randomly select a pair of nodes (u, v) as the query point.
    """
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for idx in range(total_graphs):
        num_nodes = random.randint(*node_count_range)  # Randomly generate the number of nodes

        # Generate a tree using the generate_graph function
        edges = generate_graph("tree", num_nodes)

        # Randomly choose a pair of nodes (u, v) as the query point
        u, v = random.sample(range(num_nodes), 2)

        # Save the graph to a file
        with open(f"{output_dir}/graph{idx}.txt", "w") as f:
            f.write(f"{num_nodes} {len(edges)}\n")  # Write the number of nodes and edges
            for a, b in edges:
                f.write(f"{a} {b}\n")  # Write each edge
            f.write(f"{u} {v}\n")  # Write the randomly selected node pair as the query point

    print(f"Generated {total_graphs} graphs and saved them to the '{output_dir}' directory.")


# Example usage
node_count_range = (21, 30)  # The range of node counts
total_graphs = 100  # Total number of graphs to generate
output_dir = "graph/medium/standard"  # Directory to save the graph files

generate_graphs(node_count_range, total_graphs, output_dir)