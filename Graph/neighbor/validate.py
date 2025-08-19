import os
import networkx as nx


def validate_graphs_with_query(input_dir, total_graphs):
    """
    Validate the 100 generated graphs:
    - In the first 50 graphs, the query (u, v) should have a direct edge.
    - In the last 50 graphs, the query (u, v) should not have a direct edge.
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
            u, v = map(int, f.readline().strip().split())  # Read the query pair (u, v)

        # Build the undirected graph
        G = nx.Graph()
        G.add_edges_from(edges)

        # Check if the query pair has a direct edge
        has_direct_edge = G.has_edge(u, v)

        # Validate the results
        if idx < total_graphs // 2:
            # In the first 50 graphs, the query pair (u, v) should have a direct edge
            if not has_direct_edge:
                print(f"Validation failed: In graph {idx}, query pair ({u}, {v}) should have a direct edge, but no direct edge was detected!")
        else:
            # In the last 50 graphs, the query pair (u, v) should not have a direct edge
            if has_direct_edge:
                print(f"Validation failed: In graph {idx}, query pair ({u}, {v}) should not have a direct edge, but a direct edge was detected!")

    print("Validation completed!")


# Example usage
input_dir = "./graph/easy/standard"  # Directory where the graph files are stored
total_graphs = 100  # Total number of graphs

validate_graphs_with_query(input_dir, total_graphs)