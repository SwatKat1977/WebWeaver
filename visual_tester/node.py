"""
Copyright (C) 2025  Web Weaver Development Team
SPDX-License-Identifier: GPL-3.0-or-later

This file is part of Web Weaver (https://github.com/SwatKat1977/WebWeaver).
See the LICENSE file in the project root for full license details.
"""
import wx


class Node:
    def __init__(self, id, name, pos):
        self.id = id
        self.name = name
        self.pos = wx.RealPoint(*pos)
        self.size = wx.Size(160, 100)
        self.inputs = ["In A"]
        self.outputs = ["Out A"]
        self.selected = False
        self.hovered = False

    def rect(self):
        return wx.Rect(int(self.pos.x), int(self.pos.y), self.size.width, self.size.height)
