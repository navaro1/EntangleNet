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

    remaining_instant_topology = instant_topology.copy()

    # All neighbours are entangled in instant topology (by definition of instant topology),
    # so no need to swap if source neighbours.
    paths_queue = [[source, n] for n in nx.all_neighbors(remaining_instant_topology, source)]
    adjacent_list_representation = dict(remaining_instant_topology.adjacency())
    while paths_queue:
        path = paths_queue.pop(0)
        last_node = path[-1]
        if last_node == target:
            return path

        # remove unsuccessful swaps
        for adjacent_node in list(adjacent_list_representation.get(last_node, [])):
            entanglement_swap_failure = random.random() >= q
            if entanglement_swap_failure:
                remaining_instant_topology.remove_edge(last_node, adjacent_node)
            adjacent_list_representation = dict(remaining_instant_topology.adjacency())

        for swapped_adjacent_node in adjacent_list_representation.get(last_node, []):
            new_path = list(path)
            new_path.append(swapped_adjacent_node)
            paths_queue.append(new_path)

    return None
