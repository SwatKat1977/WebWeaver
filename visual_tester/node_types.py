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
