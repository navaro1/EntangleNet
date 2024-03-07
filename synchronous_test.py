import math
import random

import pytest

from synchronous import external_phase, internal_phase
import networkx as nx

random.seed(100)  # set seed for reproducible tests


class TestExternalPhase:
    physical_topology = nx.grid_2d_graph(3, 3)

    def test_should_return_empty_graph_when_p_is_0(self):
        instant_topology = external_phase(self.physical_topology, 0)
        expected_empty_graph = nx.empty_graph()
        assert nx.utils.graphs_equal(instant_topology, expected_empty_graph)

    def test_should_return_full_topology_when_p_is_1(self):
        instant_topology = external_phase(self.physical_topology, 1)
        assert nx.utils.graphs_equal(instant_topology, self.physical_topology)

    def test_should_not_modify_instant_topology_when_modifying_physical_topology_(self):
        topology_to_be_modified = nx.grid_2d_graph(3, 3)
        instant_topology = external_phase(topology_to_be_modified, 1)
        topology_to_be_modified.add_edge((0, 0), (3, 3))
        topology_to_be_modified.remove_node((1, 1))
        assert not nx.utils.graphs_equal(instant_topology, topology_to_be_modified)
        assert instant_topology.has_node((1, 1))
        assert not instant_topology.has_edge((0, 0), (3, 3))

    @pytest.mark.parametrize("p_input", [x * 0.1 for x in range(0, 11)])
    def test_should_return_empty_topology_on_empty_physical_topology(self, p_input):
        instant_topology = external_phase(nx.empty_graph(), p_input)
        assert nx.utils.graphs_equal(instant_topology, nx.empty_graph())

    @pytest.mark.parametrize("p_input", [x * 0.1 for x in range(0, 11)])
    def test_on_average_instant_topology_should_edges_proportional_to_success_probability(self, p_input):
        number_of_runs = 100
        # A bigger graph is used, so we reduce sensitivity to low number of edges. For example with 3 by 3 grid graph,
        # we only have 12 edges so with 0.1 `p_input` we would have 1.2 edge on average, which is a 20% error.
        big_test_topology = nx.grid_2d_graph(7, 7)
        number_of_edges_physical = big_test_topology.number_of_edges()
        number_of_edges_instant_list = [external_phase(big_test_topology, p_input).number_of_edges() for _ in
                                        range(number_of_runs)]
        average_instant_edges = sum(number_of_edges_instant_list) / len(number_of_edges_instant_list)
        expected_number_of_edges = round(number_of_edges_physical * p_input)
        assert math.isclose(expected_number_of_edges, average_instant_edges, rel_tol=0.05)


class TestInternalPhase:
    source = (0, 0)  # upper left corner
    target = (2, 2)  # lower right corner
    full_instant_topology = nx.grid_2d_graph(3, 3)

    def test_should_return_none_when_instant_topology_is_empty(self):
        path = internal_phase(nx.empty_graph(), source=self.source, target=self.target, q=1.0)
        assert path is None

    def test_should_return_none_when_source_is_target(self):
        path = internal_phase(self.full_instant_topology, source=self.source, target=self.source, q=1.0)
        assert path is None

    def test_should_return_none_when_q_is_0(self):
        path = internal_phase(self.full_instant_topology, source=self.source, target=self.target, q=0)
        assert path is None

    def test_should_return_path_when_q_is_0_but_there_is_no_swap_to_happen(self):
        no_swap_instant_topology = nx.path_graph(2)  # 0 -- 1
        path = internal_phase(no_swap_instant_topology, source=0, target=1, q=0)
        assert path == [0, 1]

    def test_should_return_path_when_q_is_1_on_simple_topology(self):
        simple_instant_topology = nx.path_graph(3)  # 0 -- 1 -- 2
        path = internal_phase(simple_instant_topology, source=0, target=2, q=1)
        assert path == [0, 1, 2]

    def test_should_return_path_when_q_is_1_on_simple_tree_topology(self):
        # 0 -- 1 -- 2
        #      ' -- 3
        simple_tree_topology = nx.path_graph(3)
        simple_tree_topology.add_node(3)
        simple_tree_topology.add_edge(1, 3)
        path = internal_phase(simple_tree_topology, source=0, target=3, q=1)
        assert path == [0, 1, 3]

    def test_should_be_no_none_where_there_is_no_path(self):
        disconnected_instant_topology = nx.path_graph(3)
        disconnected_instant_topology.add_node(3)
        path = internal_phase(disconnected_instant_topology, source=0, target=3, q=1)
        assert path is None
