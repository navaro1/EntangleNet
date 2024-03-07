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
        random_number = random.random()
        if random_number > p:
            instant_topology.remove_edge(edge[0], edge[1])
    return instant_topology

# internal phase
