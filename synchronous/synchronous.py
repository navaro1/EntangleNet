import random

import networkx as nx


# external phase
def external_phase(physical_topology, p):
    if p == 0 or nx.utils.graphs_equal(physical_topology, nx.empty_graph()):
        return nx.empty_graph()
    if p == 1:
        return physical_topology.copy()
    instant_topology = physical_topology.copy()
    for edge in physical_topology.edges():
        entanglement_generation_failure = random.random() >= p
        if entanglement_generation_failure:
            instant_topology.remove_edge(edge[0], edge[1])
    return instant_topology


# internal phase
def internal_phase(instant_topology, source, target, q):
    if (source == target
            or nx.utils.graphs_equal(instant_topology, nx.empty_graph())):
        return None

    copied_instant_topology = instant_topology.copy()
    neighbours = list(nx.all_neighbors(copied_instant_topology, source))
    while len(neighbours) > 0:
        if target in neighbours:
            return True
        random_n = random.choice(neighbours)
        n_neighbours = list(nx.all_neighbors(copied_instant_topology, random_n))
        if n_neighbours == [source]:
            return False
        random_nn = random.choice(n_neighbours)
        while random_nn == source:
            random_nn = random.choice(n_neighbours)
        for n in neighbours:
            copied_instant_topology.remove_edge(source, n)
        for nn in n_neighbours:
            if nn != source:
                copied_instant_topology.remove_edge(random_n, nn)
        entanglement_swap_failure = random.random() >= q
        if entanglement_swap_failure:
            return False
        copied_instant_topology.add_edge(source, random_nn)
        neighbours = list(nx.all_neighbors(copied_instant_topology, source))
    return False


def approx_mean_path_length_for_2d_lattice(graph, source, target, check_is_lattice=True):
    if check_is_lattice and not is_2d_lattice_graph(graph):
        raise ValueError("Graph is not a 2D lattice")

    x_s, y_s = source
    x_t, y_t = target
    l1_distance = abs(x_s - x_t) + abs(y_s - y_t)  # this is also the shortest path length in 2D lattice
    all_simple_paths = list(nx.all_simple_edge_paths(graph, source=source, target=target))
    m_to_paths = {}
    for path in all_simple_paths:
        m_for_path = ((len(path) - l1_distance) / 2) + 1
        if m_for_path in m_to_paths:
            m_to_paths[m_for_path].append(path)
        else:
            m_to_paths[m_for_path] = [path]
    numerator_sum = 0
    denominator_sum = 0
    for m, paths in m_to_paths.items():
        number_of_paths = len(paths)
        path_length = len(paths[0])
        numerator_sum += number_of_paths * path_length
        denominator_sum += number_of_paths

    return numerator_sum / denominator_sum


def is_2d_lattice_graph(graph) -> bool:
    if nx.utils.graphs_equal(graph, nx.empty_graph()):
        return True
    degree_count = nx.degree_histogram(graph)
    if degree_count == [1]:  # 1 x 1 lattice
        return True

    if len(degree_count) < 2:  # Lattice with more than 1 node will have at least 2 degrees
        return False

    nodes_count = graph.number_of_nodes()
    if degree_count[1] == 2:  # We are in a 1 x N lattice:
        not_edge_nodes_count = nodes_count - 2
        return (len(degree_count) == 2  # that is for 1 x 2 lattice
                or (degree_count == [0, 2, not_edge_nodes_count]))  # that is for 1 x N lattice

    if len(degree_count) == 3 or len(degree_count) == 4:  # We are in a 2 x N lattice:
        not_corner_nodes_count = nodes_count - 4
        return (degree_count == [0, 0, 4]  # that is for 2 x 2 lattice
                or degree_count == [0, 0, 4, not_corner_nodes_count])  # that is for 2 x N lattice

    if len(degree_count) == 5:  # We are potentially in N x M lattice:
        has_four_corners = degree_count[:3] == [0, 0, 4]
        if not has_four_corners:
            return False
        has_good_number_of_nodes = degree_count[3] + degree_count[4] == nodes_count - 4
        if not has_good_number_of_nodes:
            return False
        decompositions = factor_decomposition(nodes_count)
        for rows, cols in decompositions:
            expected_number_of_degree_3_nodes = 2 * (cols - 2) + 2 * (rows - 2)
            expected_number_of_degree_4_nodes = nodes_count - 4 - expected_number_of_degree_3_nodes
            if degree_count == [0, 0, 4, expected_number_of_degree_3_nodes, expected_number_of_degree_4_nodes]:
                return True
    return False


def factor_decomposition(n):
    factors = []
    for i in range(1, int(n ** 0.5) + 1):
        if n % i == 0:
            factors.append((i, n // i))
    return factors
