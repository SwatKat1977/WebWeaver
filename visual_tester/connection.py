"""
Copyright (C) 2025  Web Weaver Development Team
SPDX-License-Identifier: GPL-3.0-or-later

This file is part of Web Weaver (https://github.com/SwatKat1977/WebWeaver).
See the LICENSE file in the project root for full license details.
"""


class Connection:
    """Represents a directional link between two node sockets.

    A connection joins an output socket on one node to an input socket
    on another. It is primarily used for visual representation within
    the node editor canvas and for maintaining the logical data flow
    between nodes.

    Attributes:
        out_node: The source node providing the output.
        out_index (int): Index of the output socket on the source node.
        in_node: The target node receiving the input.
        in_index (int): Index of the input socket on the target node.
        hovered (bool): Whether the connection is currently hovered
            by the mouse cursor (used for visual highlighting).
    """
    # pylint: disable=too-few-public-methods

    def __init__(self, out_node, out_index, in_node, in_index):
        """Initialise a new node connection.

        Args:
            out_node: The node that outputs data.
            out_index (int): The index of the output port on the source node.
            in_node: The node that receives data.
            in_index (int): The index of the input port on the target node.
        """
        self.out_node = out_node
        self.out_index = out_index
        self.in_node = in_node
        self.in_index = in_index
        self.hovered = False
