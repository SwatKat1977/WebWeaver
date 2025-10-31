class Connection:
    def __init__(self, out_node, out_index, in_node, in_index):
        self.out_node = out_node
        self.out_index = out_index
        self.in_node = in_node
        self.in_index = in_index
        self.hovered = False
