"""
Copyright (C) 2025  Web Weaver Development Team
SPDX-License-Identifier: GPL-3.0-or-later

This file is part of Web Weaver (https://github.com/SwatKat1977/WebWeaver).
See the LICENSE file in the project root for full license details.
"""
import wx
from node_types import NODE_TYPES, NodeShape, NodeCategory


class Node:
    """Represents a visual and logical node within the editor canvas.

    Each node defines its type, position, size, input and output ports,
    and rendering colours. Nodes are the fundamental building blocks
    in the node editor and can be connected using `Connection` objects.
    """
    # pylint: disable=too-few-public-methods, too-many-instance-attributes

    def __init__(self, node_id, node_type, pos):
        """Initialise a new node instance.

        Args:
            node_id (int): Unique identifier for this node.
            node_type (str): The type name of the node, used to look up
                its visual and functional properties from `NODE_TYPES`.
            pos (tuple[float, float]): The (x, y) position of the node
                in the canvas coordinate space.
        """
        t = NODE_TYPES.get(node_type, NODE_TYPES["Condition"])
        self.id = node_id
        self.name = t.type_name
        self.node_type = node_type
        self.pos = wx.RealPoint(*pos)
        self.size = wx.Size(160, 100)
        self.inputs = list(t.inputs)
        self.outputs = list(t.outputs)
        self.selected = False
        self.hovered = False
        self.color = wx.Colour(*t.color)
        self.label_color = wx.Colour(*t.label_color)
        self._shape = t.shape
        self._category = t.category

        # default size
        self.size = wx.Size(160, 100)

        # Apply special rules for specific categories
        if self.category == NodeCategory.START:
            # Smaller circular start node, output only
            self.size = wx.Size(60, 60)
            self.inputs = []  # no inputs
            self.outputs = [""]  # single output (centered)
    
        elif self.category == NodeCategory.END:
            # Smaller circular end node, input only
            self.size = wx.Size(60, 60)
            self.inputs = [""]  # single input (centered)
            self.outputs = []  # no outputs

    def rect(self):
        """Return the rectangular bounds of the node in canvas coordinates.

        Returns:
            wx.Rect: The rectangle representing the node's position and size.
        """
        return wx.Rect(int(self.pos.x), int(self.pos.y), self.size.width, self.size.height)

    def is_protected(self) -> bool:
        """Return True if this node cannot be deleted."""
        return self.category in (NodeCategory.START, NodeCategory.END)

    @property
    def shape(self) -> NodeShape:
        return self._shape

    @property
    def category(self) -> NodeCategory:
        return self._category
