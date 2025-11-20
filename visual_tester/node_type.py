"""
Copyright (C) 2025  Web Weaver Development Team
SPDX-License-Identifier: GPL-3.0-or-later

This file is part of Web Weaver (https://github.com/SwatKat1977/WebWeaver).
See the LICENSE file in the project root for full license details.
"""
from dataclasses import dataclass
import enum
from typing import List, Optional, Tuple
from node_pin import NodePin


class NodeShape(enum.Enum):
    """Enumeration of available node shapes.

    Attributes:
        RECTANGLE: A standard rectangular node shape.
        CIRCLE: A circular node shape.
    """
    RECTANGLE = "rectangle"
    CIRCLE = "circle"


class NodeCategory(enum.Enum):
    """Enumeration of logical categories a node can belong to.

    Attributes:
        NORMAL: A regular node without any special semantics.
        START: A designated starting node within a node graph or flow.
    """
    NORMAL = "normal"
    START = "start"


class NodeGroup(enum.Enum):

    EVENT = enum.auto()
    INPUT = enum.auto()
    ACTION = enum.auto()
    ASSERTION = enum.auto()
    FLOW_CONTROL = enum.auto()
    VARIABLES_AND_DATA = enum.auto()
    ERROR_HANDLER = enum.auto()


DEFAULT_NODE_FILL_COLOUR: Tuple[int, int, int] = (45, 47, 52)
DEFAULT_NODE_LABEL_COLOUR: Tuple[int, int, int] = (255, 255, 255)


@dataclass
class NodeType:

    # Display
    title: str
    node_group: NodeGroup

    # Pins
    inputs: List[NodePin]
    outputs: List[NodePin]

    # Visuals
    colour: Tuple[int, int, int] = DEFAULT_NODE_FILL_COLOUR
    label_colour: Tuple[int, int, int] = DEFAULT_NODE_LABEL_COLOUR
    header_colour: Optional[Tuple[int, int, int]] = None
    shape: NodeShape = NodeShape.RECTANGLE
    category: NodeCategory = NodeCategory.NORMAL

    # Dynamic pin behaviour
    can_add_inputs: bool = False
    can_add_outputs: bool = False

    # Versioning (future-proof)
    version: int = 1

    def __post_init__(self):
        if self.header_colour is None:
            # default: darker version of main color
            r, g, b = self.colour
            self.header_colour = (max(0, r-20), max(0, g-20), max(0, b-20))
