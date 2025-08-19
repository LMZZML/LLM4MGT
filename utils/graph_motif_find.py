import random


def build_adjacency_list(edges):
    adj_list = {}
    for u, v in edges:
        if u not in adj_list:
            adj_list[u] = []
        if v not in adj_list:
            adj_list[v] = []
        adj_list[u].append(v)
        adj_list[v].append(u)
    return adj_list


def calculate_degree_sum(path, adj_list):
    return sum(len(adj_list[node]) for node in path)


def find_length_two_paths(edges):
    adj_list = build_adjacency_list(edges)
    length_two_paths = []
    for u in adj_list:
        for v in adj_list[u]:
            for w in adj_list[v]:
                if w != u:
                    length_two_paths.append([u, v, w])
    random.shuffle(length_two_paths)
    return length_two_paths


def find_length_three_paths(edges):
    adj_list = build_adjacency_list(edges)
    length_three_paths = []
    for u in adj_list:
        for v in adj_list[u]:
            if v == u:
                continue
            for w in adj_list[v]:
                if w == u or w == v:
                    continue
                for x in adj_list[w]:
                    if x == u or x == v or x == w:
                        continue
                    length_three_paths.append([u, v, w, x])
    random.shuffle(length_three_paths)
    return length_three_paths


def find_length_four_paths(edges):
    adj_list = build_adjacency_list(edges)
    length_four_paths = []
    for u in adj_list:
        for v in adj_list[u]:
            if v == u:
                continue
            for w in adj_list[v]:
                if w == u or w == v:
                    continue
                for x in adj_list[w]:
                    if x == u or x == v or x == w:
                        continue
                    for y in adj_list[x]:
                        if y == u or y == v or y == w or y == x:
                            continue
                        length_four_paths.append([u, v, w, x, y])
    random.shuffle(length_four_paths)
    return length_four_paths


def find_paths(edges, length):
    adj_list = build_adjacency_list(edges)
    result = []

    def dfs(path):
        if len(path) == length:
            result.append(path[:])
            return

        current_node = path[-1]
        for neighbor in adj_list[current_node]:
            if neighbor not in path:
                path.append(neighbor)
                dfs(path)
                path.pop()

    for start_node in adj_list:
        dfs([start_node])

    return result


def find_cycles(edges, k):
    def dfs(node, start, visited, path, adj_list, cycles):
        if len(path) > k:
            return
        for neighbor in adj_list[node]:
            if neighbor == start and len(path) > 2:
                cycles.add(tuple(sorted(path)))
            elif neighbor not in visited:
                visited.add(neighbor)
                dfs(neighbor, start, visited, path + [neighbor], adj_list, cycles)
                visited.remove(neighbor)

    adj_list = build_adjacency_list(edges)
    cycles = set()
    for node in adj_list:
        dfs(node, node, set([node]), [node], adj_list, cycles)
    cycles = list(cycles)
    random.shuffle(cycles)
    sorted_cycles = sorted(cycles, key=len, reverse=True)
    return sorted_cycles