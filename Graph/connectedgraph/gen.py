import networkx as nx
import random
from networkx import Graph
import os
import sys

# Get the root directory of the project
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)
from utils.gen import generate_graph


def generate_graphs(node_count_range, total_graphs, output_dir):
    """
    Use the generate_graph function to generate 100 graphs, half as a single connected graph and half as a forest.
    """
    half = total_graphs // 2  # Half of the graphs will be a single connected graph, the other half a forest
    graphs = []

    # Create the output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for i in range(total_graphs):
        num_nodes = random.randint(*node_count_range)  # Randomly generate the number of nodes

        if i < half:
            edges = generate_graph("connected", num_nodes)
        else:
            num_components = random.randint(2, min(max(2, num_nodes // 3), 4))
            edges = generate_graph("disconnected", num_nodes, num_components)

        # Convert to NetworkX graph object
        G = Graph()
        G.add_edges_from(edges)

        graphs.append(G)
        # print(i)

    # Save all graphs to files
    for idx, G in enumerate(graphs):
        with open(f"{output_dir}/graph{idx}.txt", "w") as f:
            f.write(f"{len(G.nodes)} {len(G.edges)}\n")  # Write the number of nodes and edges
            for u, v in G.edges:
                f.write(f"{u} {v}\n")  # Write each edge

    print(f"Generated {total_graphs} graphs and saved them to the '{output_dir}' directory.")


# Example usage
node_count_range = (31, 40)  # Range of node count
total_graphs = 100  # Total number of graphs to generate
output_dir = "graph/hard/standard"  # Directory to save the graph files

generate_graphs(node_count_range, total_graphs, output_dir)