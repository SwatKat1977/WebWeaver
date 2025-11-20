"""
Copyright (C) 2025  Web Weaver Development Team
SPDX-License-Identifier: GPL-3.0-or-later

This file is part of Web Weaver (https://github.com/SwatKat1977/WebWeaver).
See the LICENSE file in the project root for full license details.
"""
import wx
from node_type import NodeShape, NodeCategory
from node_registry import NodeRegistry


class Node:
    """
    Represents a visual and logical node within the editor canvas.

    Nodes are the primary building blocks of the node editor. Each node has
    a unique ID, a type (mapped from ``NODE_TYPES``), a position, size,
    input/output ports, visual styling, and optional behavioural categories.

    Nodes can be connected via ``Connection`` objects, rendered on the canvas,
    and interacted with (selected, hovered, moved). Special rules may apply
    depending on a node's category; for example, ``NodeCategory.START`` nodes
    are circular, smaller, and cannot be deleted.

    Attributes:
        id (int): Unique identifier for the node.
        name (str): Human-readable node name from its type definition.
        node_type (str): Type key used to look up metadata in ``NODE_TYPES``.
        pos (wx.RealPoint): The (x, y) position of the node in canvas space.
        size (wx.Size): The width and height of the node for rendering.
        inputs (list[str]): List of input port labels.
        outputs (list[str]): List of output port labels.
        selected (bool): Whether the node is currently selected in the UI.
        hovered (bool): Whether the mouse cursor is currently over the node.
        color (wx.Colour): Primary fill colour of the node.
        label_color (wx.Colour): Colour used for the node's text.
        _shape (NodeShape): Visual shape (rectangle or circle).
        _category (NodeCategory): Logical category (e.g., ``START`` or
                                  ``NORMAL``).

    Category-specific behaviour:
        - ``NodeCategory.START`` nodes:
            * Are circular by default.
            * Are smaller (60×60 px).
            * Have no input ports.
            * Have a single centred output port.
            * Are protected from deletion via ``is_protected()``.

    The node's rendered rectangle can be retrieved using ``rect()``, and
    convenience properties ``shape`` and ``category`` expose the node's
    metadata.
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
        self.type = NodeRegistry.get(node_type)

        self.id = node_id
        self.title = self.type.title
        self.type_name = node_type
        self.pos = wx.RealPoint(*pos)
        self.size = wx.Size(160, 100)
        self.selected = False
        self.hovered = False
        self._inputs = self.type.inputs
        self._outputs = self.type.outputs

        # default size
        self.size = wx.Size(160, 100)

        # Apply special rules for specific categories
        if self.category == NodeCategory.START:
            # Smaller circular start node, output only
            self.size = wx.Size(60, 60)

    @property
    def inputs(self):
        return self._inputs

    @property
    def outputs(self):
        return self._outputs

    def rect(self):
        """
        Return the rectangular bounds of the node in canvas coordinates.

        The rectangle is computed directly from the node's position and size,
        and is used for rendering, hit-testing, and interaction logic within
        the editor.

        Returns:
            wx.Rect: A rectangle representing the node's position and size.
        """
        return wx.Rect(int(self.pos.x), int(self.pos.y), self.size.width, self.size.height)

    def is_protected(self) -> bool:
        """
        Determine whether this node is protected from deletion.

        A node is considered protected if it belongs to a special category
        such as ``NodeCategory.START``. Protected nodes cannot be removed
        from the canvas by user actions.

        Returns:
            bool: ``True`` if this node should not be deleted, ``False``
                  otherwise.
        """
        return self.category == NodeCategory.START

    @property
    def shape(self) -> NodeShape:
        """
        The visual shape of the node.

        The shape influences how the node is drawn on the canvas (e.g.,
        rectangular or circular). This value is defined by the node's
        metadata entry within ``NODE_TYPES``.

        Returns:
            NodeShape: The enum value representing the node's visual shape.
        """
        return self.type.shape

    @property
    def category(self) -> NodeCategory:
        """
        The logical category assigned to this node.

        The category determines special behavioural rules (e.g. whether
        the node is a start node, or whether it can be deleted). It is
        defined by the node's metadata from ``NODE_TYPES``.

        Returns:
            NodeCategory: The enum value representing the node's category.
        """
        return self.type.category

    def auto_size(self, gc):
        font = wx.Font(
            10,
            wx.FONTFAMILY_DEFAULT,
            wx.FONTSTYLE_NORMAL,
            wx.FONTWEIGHT_BOLD
        )

        # Must include text colour when using GraphicsContext
        gc.SetFont(font, wx.Colour(255, 255, 255))

        text_w, text_h, _, _ = gc.GetFullTextExtent(self.title)

        padding = 40
        min_width = 120

        new_width = int(max(min_width, text_w + padding))

        # Apply size change
        self.size = wx.Size(new_width, self.size.height)

