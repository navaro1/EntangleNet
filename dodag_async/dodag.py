class AsyncSchemeBase:
    def __init__(self):
        pass

    def navigate(self, previous_node, next_node):
        raise NotImplementedError()

    def join_network(self):
        raise NotImplementedError()

    def direct_neighbours(self):
        raise NotImplementedError()

    def instant_neighbours(self):
        raise NotImplementedError()


class DodagAsyncNode(AsyncSchemeBase):
    def __init__(self, node_id, direct_links=None, parent=None, rank=float('inf')):
        super().__init__()
        if direct_links is None:
            direct_links = []
        self.node_id = node_id
        self.direct_links = direct_links
        self.parent = parent
        self.rank = rank

    def navigate(self, previous_node, next_node):
        return self.parent

    def join_network(self):
        raise NotImplementedError()

    def direct_neighbours(self):
        raise NotImplementedError()

    def instant_neighbours(self):
        raise NotImplementedError()

    def is_root(self):
        return self.parent is None

    # sending 'dio' is asking: 'do you want to join us?',
    def send_dio(self):
        for neighbour in self.direct_links:
            neighbour.receive_dio(self)

    def receive_dio(self, potential_parent_node):
        if self.rank is None or self.rank > potential_parent_node.rank + 1:
            self.parent = potential_parent_node
            self.rank = potential_parent_node.rank + 1
            potential_parent_node.receive_dao(self)

    # sending 'dao' is saying: 'Yes, I want to join you'
    def receive_dao(self, calling_node):
        pass

    # sending 'dis' are you in dodag?
