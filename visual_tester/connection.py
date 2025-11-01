"""
Copyright (C) 2025  Web Weaver Development Team
SPDX-License-Identifier: GPL-3.0-or-later

This file is part of Web Weaver (https://github.com/SwatKat1977/WebWeaver).
See the LICENSE file in the project root for full license details.
"""


class Connection:
    def __init__(self, out_node, out_index, in_node, in_index):
        self.out_node = out_node
        self.out_index = out_index
        self.in_node = in_node
        self.in_index = in_index
        self.hovered = False
