import networkx as nx


class AsyncSchemeBase:
    def __init__(self):
        pass

    def navigate(self, previous_node, next_node):
        raise NotImplementedError()

    def join_network(self):
        raise NotImplementedError()

    def direct_neighbours(self):
        raise NotImplementedError()

    def get_instant_neighbours(self):
        raise NotImplementedError()


DodagAttributeName = 'dodag_details'


class DodagAsyncNode(AsyncSchemeBase):

    @classmethod
    def construct_dodag_on_network(cls, physical_network: nx.Graph, root_node_id):
        for node in physical_network.nodes:
            neighbours_ids = list(nx.neighbors(physical_network, node))
            neighbours_nodes = [physical_network.nodes[neighbour] for neighbour in neighbours_ids]
            rank = 0 if node == root_node_id else float('inf')
            node_details = DodagAsyncNode(node_id=node, direct_links=neighbours_nodes, parent=None, rank=rank)
            nx.set_node_attributes(physical_network, {node: {DodagAttributeName: node_details}})

    def __init__(self, node_id, direct_links=None, parent=None, rank=float('inf')):
        super().__init__()
        if direct_links is None:
            direct_links = []
        self.direct_links = direct_links
        self.node_id = node_id
        self.parent = parent
        self.rank = rank
        self.instant_neighbours = []

    def __eq__(self, other):
        return (self.node_id == other.node_id
                and self.direct_links == other.direct_links
                and self.parent == other.parent
                and self.rank == other.rank)

    def navigate(self, previous_node, next_node):
        return self.parent

    def join_network(self):
        for neighbour in self.direct_links:
            self.receive_dio(neighbour[DodagAttributeName])

    def direct_neighbours(self):
        raise NotImplementedError()

    def get_instant_neighbours(self):
        return self.instant_neighbours

    def is_root(self):
        return self.parent is None

    # sending 'dio' is asking: 'do you want to join us?',
    def send_dis(self):
        for neighbour in self.direct_links:
            neighbour[DodagAttributeName].receive_dio(self)

    def receive_dio(self, potential_parent_node):
        if self.rank is None or self.rank > potential_parent_node.rank + 1:
            self.parent = potential_parent_node
            self.rank = potential_parent_node.rank + 1
            potential_parent_node.receive_dao(self)

    # sending 'dao' is saying: 'Yes, I want to join you'
    def receive_dao(self, calling_child_node):
        self.instant_neighbours.append(calling_child_node)
        calling_child_node.instant_neighbours.append(self)
        pass

    # sending 'dis' are you in dodag?


################

import random
import uuid
#
# class Node:
#     def __init__(self, node_id):
#         self.node_id = node_id
#         self.parent = None
#         self.children = set()
#         self.rank = float('inf')
#         self.version = 0
#
#     def join_dodag(self, parent_node):
#         """
#         Called by a child node to join the DODAG by attaching to a parent node.
#         """
#         self.parent = parent_node
#         self.rank = parent_node.rank + 1
#         self.version = parent_node.version
#         parent_node.add_child(self)
#
#     def add_child(self, child_node):
#         """
#         Called by a parent node to add a child node to its set of children.
#         """
#         self.children.add(child_node)
#
#     def remove_child(self, child_node):
#         """
#         Called by a parent node to remove a child node from its set of children.
#         """
#         self.children.discard(child_node)
#
#     def disconnect(self):
#         """
#         Called by a node to disconnect from the DODAG.
#         Removes the node from its parent's children set and resets its own properties.
#         """
#         if self.parent:
#             self.parent.remove_child(self)
#         self.parent = None
#         self.rank = float('inf')
#         self.version = 0
#
#     def is_in_dodag(self):
#         """
#         Checks if the node is currently part of the DODAG.
#         Returns True if the node has a parent, False otherwise.
#         """
#         return self.parent is not None
#
#     def dao(self):
#         """
#         Destination Advertisement Object (DAO) operation.
#         Called by a child node to send a DAO message to its parent.
#         The DAO message contains the child node's information.
#     """
#     if self.parent:
#         # Send DAO message to the parent node
#         self.parent.receive_dao(self)
#
# def receive_dao(self, child_node):
#     """
#     Called by a parent node to receive a DAO message from a child node.
#     Updates the parent node's information about the child node.
#     """
#     self.add_child(child_node)
#
# def dio(self):
#     """
#     DODAG Information Object (DIO) operation.
#     Called by a parent node to send a DIO message to its children.
#     The DIO message contains the parent node's rank and version.
#     """
#     for child in self.children:
#         # Send DIO message to each child node
#         child.receive_dio(self.rank, self.version)
#
# def receive_dio(self, parent_rank, parent_version):
#     """
#     Called by a child node to receive a DIO message from its parent.
#     Updates the child node's rank and version based on the parent's information.
#     """
#     if parent_version > self.version:
#         self.rank = parent_rank + 1
#         self.version = parent_version
#
# def dis(self):
#     """
#     DODAG Information Solicitation (DIS) operation.
#     Called by a node to request DIO messages from neighboring nodes.
#     Broadcasts the DIS message to all neighboring nodes.
#     """
#     # Broadcast DIS message to neighboring nodes
#     for neighbor in self.get_neighbors():
#         neighbor.receive_dis(self)
#
# def receive_dis(self, node):
#     """
#     Called by a node to receive a DIS message from a neighboring node.
#     Sends a DIO message back to the requesting node.
#     """
#     self.dio()
#
# def get_neighbors(self):
#     """
#     Returns a set of neighboring nodes.
#     In this implementation, it returns a random subset of nodes.
#     In a real scenario, this would be based on network topology.
#     """
#     all_nodes = [node for node in nodes if node != self]
#     num_neighbors = random.randint(1, len(all_nodes))
#     return random.sample(all_nodes, num_neighbors)


# Create a set of nodes
# nodes = [Node(uuid.uuid4()) for _ in range(10)]
#
# # Randomly establish parent-child relationships
# for node in nodes:
#     if not node.is_in_dodag() and random.random() < 0.7:
#         parent = random.choice([n for n in nodes if n.is_in_dodag()])
#         node.join_dodag(parent)
#
# # Perform DODAG operations
# for node in nodes:
#     if node.is_in_dodag():
#         node.dao()  # Child nodes send DAO messages to their parents
#         node.dio()  # Parent nodes send DIO messages to their children
#     else:
#         node.dis()  # Disconnected nodes send DIS messages to request DIO messages
#
# # Randomly disconnect some nodes
# for node in nodes:
#     if node.is_in_dodag() and random.random() < 0.3:
#         node.disconnect()
#
# # Check if nodes are in the DODAG
# for node in nodes:
#     print(f"Node {node.node_id} is in DODAG: {node.is_in_dodag()}")
