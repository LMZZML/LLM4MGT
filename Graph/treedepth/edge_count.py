import os

def read_graph_metadata(file_path):
    """
    Reads the first line of a graph file to extract the number of nodes and edges.

    Args:
        file_path (str): Path to the graph file.

    Returns:
        tuple: (number_of_nodes, number_of_edges)
    """
    with open(file_path, "r") as f:
        # Read the first line and extract n, m
        line = f.readline().strip()
        n, m = map(int, line.split())
        return n, m

def calculate_averages_from_files(input_dir, num_files):
    """
    Calculates average number of nodes and edges from the first `num_files` graph files.

    Args:
        input_dir (str): Directory containing graph files.
        num_files (int): Number of files to process.

    Returns:
        tuple: (average_nodes, average_edges)
    """
    total_nodes = 0
    total_edges = 0
    processed_files = 0

    for idx in range(num_files):
        file_path = os.path.join(input_dir, f"graph{idx}.txt")
        if os.path.isfile(file_path):  # Ensure the file exists
            num_nodes, num_edges = read_graph_metadata(file_path)
            total_nodes += num_nodes
            total_edges += num_edges
            processed_files += 1

    if processed_files == 0:
        raise ValueError("No valid graph files found in the directory.")

    return total_nodes / processed_files, total_edges / processed_files

# Parameters
input_dir = "./graph/easy/standard"  # Directory containing graph files
num_files = 100  # Number of files to process

# Calculate averages
average_nodes, average_edges = calculate_averages_from_files(input_dir, num_files)

# Output the results
print(f"Average number of nodes and edges: {average_nodes:.2f}/{average_edges:.2f}")

input_dir = "graph/easy/standard"  # Directory containing graph files
num_files = 100  # Number of files to process

# Calculate averages
average_nodes, average_edges = calculate_averages_from_files(input_dir, num_files)

# Output the results
print(f"Average number of nodes and edges: {average_nodes:.2f}/{average_edges:.2f}")


input_dir = "graph/medium/standard"  # Directory containing graph files
num_files = 100  # Number of files to process

# Calculate averages
average_nodes, average_edges = calculate_averages_from_files(input_dir, num_files)

# Output the results
print(f"Average number of nodes and edges: {average_nodes:.2f}/{average_edges:.2f}")


input_dir = "graph/hard/standard"  # Directory containing graph files
num_files = 100  # Number of files to process

# Calculate averages
average_nodes, average_edges = calculate_averages_from_files(input_dir, num_files)

# Output the results
print(f"Average number of nodes and edges: {average_nodes:.2f}/{average_edges:.2f}")