import os
import networkx as nx


def validate_graphs_with_query(input_dir, total_graphs):
    """
    Validate the generated 100 graphs:
    - For the first 50 graphs, the query (u, v) should be connected.
    - For the last 50 graphs, the query (u, v) should be disconnected.
    """
    for idx in range(total_graphs):
        file_path = os.path.join(input_dir, f"graph{idx}.txt")

        # Check if the file exists
        if not os.path.exists(file_path):
            print(f"Graph file {file_path} does not exist!")
            continue

        # Read graph data
        with open(file_path, "r") as f:
            num_nodes, num_edges = map(int, f.readline().strip().split())
            edges = []
            for _ in range(num_edges):
                u, v = map(int, f.readline().strip().split())
                edges.append((u, v))
            u, v = map(int, f.readline().strip().split())  # Read the query pair (u, v)

        # Construct the undirected graph
        G = nx.Graph()
        G.add_edges_from(edges)

        # Check if the query pair is connected
        is_connected_query = nx.has_path(G, u, v)

        # Validate the result
        if idx < total_graphs // 2:
            # For the first 50 graphs, the query pair (u, v) should be connected
            if not is_connected_query:
                print(f"Validation failed: In graph {idx}, the query pair ({u}, {v}) should be connected, but it is not!")
        else:
            # For the last 50 graphs, the query pair (u, v) should not be connected
            if is_connected_query:
                print(f"Validation failed: In graph {idx}, the query pair ({u}, {v}) should not be connected, but it is!")

    print("Validation complete!")


# Example usage
input_dir = "graph/hard/standard"  # Directory containing the graph files
total_graphs = 100  # Total number of graphs

validate_graphs_with_query(input_dir, total_graphs)