import random


def generate_graph(graph_type, num_nodes, num_components=None):
    if graph_type == "tree":
        edges = []
        for i in range(1, num_nodes):
            u = i
            v = random.randint(0, i - 1)
            edges.append(tuple(sorted((u, v))))
        return edges

    elif graph_type == "connected":
        edges = generate_graph("tree", num_nodes)
        total_edges = random.randint(min(num_nodes * (num_nodes - 1) // 2, num_nodes), max(min(num_nodes * (num_nodes - 1) // 2, num_nodes * 3), num_nodes * (num_nodes - 1) // 4))
        edge_set = set(edges)

        while len(edge_set) < total_edges:
            u = random.randint(0, num_nodes - 1)
            v = random.randint(0, num_nodes - 1)
            if u != v:
                edge_set.add(tuple(sorted((u, v))))

        return sorted(edge_set)

    elif graph_type == "disconnected":
        if num_components is None or num_components < 2:
            raise ValueError("disconnected graph requires at least two components")
        if num_nodes < num_components * 2:
            raise ValueError("insufficient nodes for at least two nodes per component")

        remaining_nodes = num_nodes - num_components * 2
        if remaining_nodes < 0:
            raise ValueError("insufficient nodes to satisfy the condition")

        segment_sizes = [2] * num_components
        for _ in range(remaining_nodes):
            idx = random.randint(0, num_components - 1)
            segment_sizes[idx] += 1

        node_pool = list(range(num_nodes))
        random.shuffle(node_pool)
        components = []
        start = 0
        for size in segment_sizes:
            components.append(node_pool[start:start + size])
            start += size

        edges = []
        for component in components:
            subgraph_edges = generate_graph("connected", len(component))
            component_map = {i: node for i, node in enumerate(component)}
            edges += [tuple(sorted((component_map[u], component_map[v]))) for u, v in subgraph_edges]

        return sorted(edges)

    elif graph_type == "forest":
        if num_components is None or num_components < 1:
            raise ValueError("forest type requires at least one tree")
        if num_nodes < num_components:
            raise ValueError("insufficient nodes to generate specified number of trees")

        remaining_nodes = num_nodes - num_components
        segment_sizes = [1] * num_components
        for _ in range(remaining_nodes):
            idx = random.randint(0, num_components - 1)
            segment_sizes[idx] += 1

        node_pool = list(range(num_nodes))
        random.shuffle(node_pool)
        components = []
        start = 0
        for size in segment_sizes:
            components.append(node_pool[start:start + size])
            start += size

        edges = []
        for component in components:
            subgraph_edges = generate_graph("tree", len(component))
            component_map = {i: node for i, node in enumerate(component)}
            edges += [tuple(sorted((component_map[u], component_map[v]))) for u, v in subgraph_edges]

        return sorted(edges)

    else:
        raise ValueError("Unknown graph type: specify 'tree', 'connected', 'disconnected', or 'forest'")