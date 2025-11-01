"""
Copyright (C) 2025  Web Weaver Development Team
SPDX-License-Identifier: GPL-3.0-or-later

This file is part of Web Weaver (https://github.com/SwatKat1977/WebWeaver).
See the LICENSE file in the project root for full license details.
"""
import wx
from node_types import NODE_TYPES


class Node:
    def __init__(self, node_id, node_type, pos):
        t = NODE_TYPES.get(node_type, NODE_TYPES["Condition"])
        self.id = node_id
        self.name = t.type_name
        self.node_type = node_type
        self.pos = wx.RealPoint(*pos)
        self.size = wx.Size(160, 100)
        self.inputs = ["In A"]
        self.outputs = ["Out A"]
        self.selected = False
        self.hovered = False
        self.color = wx.Colour(*t.color)
        self.label_color = wx.Colour(*t.label_color)

    def rect(self):
        return wx.Rect(int(self.pos.x), int(self.pos.y), self.size.width, self.size.height)
