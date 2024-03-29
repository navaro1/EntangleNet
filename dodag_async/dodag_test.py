import networkx as nx
import pytest

from dodag import AsyncSchemeBase, DodagAsyncNode, DodagAttributeName


class TestAsyncSchemeBase:
    def test_navigate_should_raise_not_implemented_error(self):
        base = AsyncSchemeBase()
        with pytest.raises(NotImplementedError):
            base.navigate(0, 1)

    def test_join_network_should_raise_not_implemented_error(self):
        base = AsyncSchemeBase()
        with pytest.raises(NotImplementedError):
            base.join_network()

    def test_direct_links_should_raise_not_implemented_error(self):
        base = AsyncSchemeBase()
        with pytest.raises(NotImplementedError):
            base.direct_neighbours()

    def test_instant_links_should_raise_not_implemented_error(self):
        base = AsyncSchemeBase()
        with pytest.raises(NotImplementedError):
            base.get_instant_neighbours()


class TestDodagAsyncScheme:
    def test_should_have_node_id_field(self):
        expected_name = "this is my name"
        scheme = DodagAsyncNode(node_id=expected_name)
        assert scheme.node_id == expected_name

    def test_should_have_direct_links_field(self):
        expected_direct_links = [1, 2, 3]
        scheme = DodagAsyncNode(node_id="do_not_care", direct_links=expected_direct_links)
        assert scheme.direct_links == expected_direct_links

    def test_should_have_parent_field(self):
        expected_parent = "parent"
        scheme = DodagAsyncNode(node_id="do_not_care", parent=expected_parent)
        assert scheme.parent == expected_parent

    def test_should_have_rank_field(self):
        expected_rank = 123
        scheme = DodagAsyncNode(node_id="do_not_care", rank=expected_rank)
        assert scheme.rank == expected_rank

    @pytest.mark.parametrize("previous_node, next_node", [(123, 123), (100, 2), ("2", 3)])
    def test_navigate_should_return_parent(self, previous_node, next_node):
        expected_parent = "parent"
        scheme = DodagAsyncNode(node_id="do_not_care", parent=expected_parent)
        assert scheme.navigate(previous_node, expected_parent) == expected_parent

    @pytest.mark.parametrize("parent, expected", [(None, True), (123, False), ("parent", False)])
    def test_is_root_should_return_true_if_parent_is_none(self, parent, expected):
        scheme = DodagAsyncNode(node_id="do_not_care", parent=parent)
        assert scheme.is_root() is expected

    def test_send_dio_should_call_receive_dio_on_neighbours(self):
        n1 = _DodagAsyncNodeTest(node_id="neighbour1")
        n2 = _DodagAsyncNodeTest(node_id="neighbour2")
        neighbours = [{DodagAttributeName: n1}, {DodagAttributeName: n2}]
        node_under_test = DodagAsyncNode(node_id="node_under_test", direct_links=neighbours)
        node_under_test.send_dis()
        assert n1.called_dio_with == node_under_test
        assert n2.called_dio_with == node_under_test

    @pytest.mark.parametrize("test_rank, non_parent_rank", [(2, 2), (2, 3), (2, 1)])
    def test_receive_dio_should_not_modify_rank_not_call_dao_when_arg_has_lower_rank(self, test_rank, non_parent_rank):
        node_under_test = _DodagAsyncNodeTest(node_id="node_under_test", rank=test_rank)
        node_with_lower_rank = _DodagAsyncNodeTest(node_id="non_parent_node", rank=non_parent_rank)
        node_under_test.receive_dio(node_with_lower_rank)
        assert node_under_test.rank == 2
        assert node_with_lower_rank.last_dao_call_arg is None

    def test_receive_dao_should_modify_rank_parent_and_call_dao_when_has_lower_rank(self):
        old_parent_node = _DodagAsyncNodeTest(node_id="old_parent", rank=6)
        node_under_test = _DodagAsyncNodeTest(node_id="node_under_test", rank=7, parent=old_parent_node)
        new_parent_node = _DodagAsyncNodeTest(node_id="new_parent", rank=4)
        node_under_test.receive_dio(new_parent_node)
        assert node_under_test.rank == 5
        assert node_under_test.parent == new_parent_node
        assert new_parent_node.last_dao_call_arg == node_under_test

    def test_construct_dodag_should_initialize_async_nodes_and_return_root_node(self):
        physical_network = nx.grid_2d_graph(3, 3)
        root_node_id = (1, 1)
        DodagAsyncNode.construct_dodag_on_network(physical_network, root_node_id=root_node_id)
        root_node = physical_network.nodes[root_node_id]
        actual_dodag_details = root_node[DodagAttributeName]
        expected_dodag_details = DodagAsyncNode(node_id=root_node_id,
                                                direct_links=[physical_network.nodes[(0, 1)],
                                                              physical_network.nodes[(2, 1)],
                                                              physical_network.nodes[(1, 0)],
                                                              physical_network.nodes[(1, 2)]],
                                                parent=None, rank=0, )
        assert actual_dodag_details == expected_dodag_details
        # Now for every other node
        for node in physical_network.nodes:
            if node == root_node_id:
                continue
            actual_dodag_details = physical_network.nodes[node][DodagAttributeName]
            expected_dodag_details = DodagAsyncNode(node_id=node,
                                                    direct_links=[physical_network.nodes[node] for node in
                                                                  nx.neighbors(physical_network, node)],
                                                    parent=None, rank=float('inf'))
            assert actual_dodag_details == expected_dodag_details

    def test_should_join_one_node_scenario(self):
        physical_network = nx.grid_2d_graph(3, 3)
        root_node_id = (1, 1)
        one_below_node_id = (2, 1)
        DodagAsyncNode.construct_dodag_on_network(physical_network, root_node_id=root_node_id)
        root_node = physical_network.nodes[root_node_id]
        one_below_node = physical_network.nodes[one_below_node_id]
        one_below_node_dodag = one_below_node[DodagAttributeName]
        root_node_dodag = root_node[DodagAttributeName]
        one_below_node_dodag.join_network()
        assert one_below_node_dodag.parent == root_node_dodag
        assert one_below_node_dodag.rank == 1
        assert one_below_node_dodag.get_instant_neighbours() == [root_node_dodag]
        assert root_node_dodag.get_instant_neighbours() == [one_below_node_dodag]

    def test_should_join_two_node_scenario(self):
        physical_network = nx.grid_2d_graph(3, 3)
        root_node_id = (1, 1)
        one_below_node_id = (2, 1)
        one_below_node_id_2 = (2, 2)
        DodagAsyncNode.construct_dodag_on_network(physical_network, root_node_id=root_node_id)
        root_node = physical_network.nodes[root_node_id]
        one_below_node = physical_network.nodes[one_below_node_id]
        one_below_node_2 = physical_network.nodes[one_below_node_id_2]
        one_below_node_dodag = one_below_node[DodagAttributeName]
        one_below_node_dodag_2 = one_below_node_2[DodagAttributeName]
        root_node_dodag = root_node[DodagAttributeName]
        one_below_node_dodag.join_network()
        one_below_node_dodag_2.join_network()
        assert one_below_node_dodag.parent == root_node_dodag
        assert one_below_node_dodag_2.parent == one_below_node_dodag
        assert one_below_node_dodag.rank == 1
        assert one_below_node_dodag_2.rank == 2
        assert one_below_node_dodag.get_instant_neighbours() == [root_node_dodag, one_below_node_dodag_2]
        assert one_below_node_dodag_2.get_instant_neighbours() == [one_below_node_dodag]
        assert root_node_dodag.get_instant_neighbours() == [one_below_node_dodag]


class _DodagAsyncNodeTest(DodagAsyncNode):
    def __init__(self, node_id, direct_links=None, parent=None, rank=float('inf')):
        super().__init__(node_id, direct_links, parent, rank)
        self.called_dio_with = None
        self.last_dao_call_arg = None

    def receive_dio(self, potential_parent_node):
        super().receive_dio(potential_parent_node)
        self.called_dio_with = potential_parent_node

    def receive_dao(self, calling_child_node):
        super().receive_dao(calling_child_node)
        self.last_dao_call_arg = calling_child_node
