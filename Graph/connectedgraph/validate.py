import os
import networkx as nx


def validate_graphs(input_dir, total_graphs):
    """
    Validate the generated 100 graphs:
    - The first 50 graphs should be connected graphs.
    - The last 50 graphs should be disconnected graphs.
    """
    for idx in range(total_graphs):
        file_path = os.path.join(input_dir, f"graph{idx}.txt")

        # Check if the file exists
        if not os.path.exists(file_path):
            print(f"Graph file {file_path} does not exist!")
            continue

        # Read the graph data
        with open(file_path, "r") as f:
            num_nodes, num_edges = map(int, f.readline().strip().split())
            edges = []
            for _ in range(num_edges):
                u, v = map(int, f.readline().strip().split())
                edges.append((u, v))

        # Build the undirected graph
        G = nx.Graph()
        G.add_edges_from(edges)

        # Check if the graph is connected
        is_connected = nx.is_connected(G)

        # Validate the result
        if idx < total_graphs // 2:
            # The first 50 should be connected graphs
            if not is_connected:
                print(f"Validation failed: Graph {idx} should be connected, but it was found to be disconnected!")
        else:
            # The last 50 should be disconnected graphs
            if is_connected:
                print(f"Validation failed: Graph {idx} should be disconnected, but it was found to be connected!")

    print("Validation completed!")


# Example usage
input_dir = "graph/medium/standard"  # Directory of graph files
total_graphs = 100  # Total number of graphs

validate_graphs(input_dir, total_graphs)