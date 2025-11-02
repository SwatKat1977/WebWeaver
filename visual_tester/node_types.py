"""
Copyright (C) 2025  Web Weaver Development Team
SPDX-License-Identifier: GPL-3.0-or-later

This file is part of Web Weaver (https://github.com/SwatKat1977/WebWeaver).
See the LICENSE file in the project root for full license details.
"""
from dataclasses import dataclass
from typing import List, Tuple

@dataclass
class NodeType:
    """Defines the structural and visual properties of a node type.

    Each node type specifies its display name, input and output ports,
    and visual colours used when rendering in the node editor. Instances
    of this class are used to describe the available node archetypes in
    the editor.

    Attributes:
        type_name (str): Display name of the node type.
        inputs (List[str]): List of input socket names for this node type.
        outputs (List[str]): List of output socket names for this node type.
        color (Tuple[int, int, int]): RGB tuple representing the node body
            colour. Defaults to a neutral grey tone.
        label_color (Tuple[int, int, int]): RGB tuple for the text label colour.
            Defaults to white.
    """
    type_name: str
    inputs: List[str]
    outputs: List[str]
    color: Tuple[int, int, int] = (45, 47, 52)  # default fill colour
    label_color: Tuple[int, int, int] = (255, 255, 255)


# Registry of available node types
NODE_TYPES = {
    "Start": NodeType("Start", [], ["Next"], (40, 90, 180)),
    "Condition": NodeType("Condition", ["Input"], ["True", "False"], (70, 70, 80)),
    "Action": NodeType("Action", ["Trigger"], ["Done"], (90, 60, 120)),
    "End": NodeType("End", ["Input"], [], (160, 50, 50)),
}
"""dict[str, NodeType]: A global registry of all predefined node types.

Each key is the internal name of a node type, and each value is a
`NodeType` instance defining that node’s structure and colours.
This registry is used by the editor to create new nodes of a given type.
"""
