"""
Copyright (C) 2025  Web Weaver Development Team
SPDX-License-Identifier: GPL-3.0-or-later

This file is part of Web Weaver (https://github.com/SwatKat1977/WebWeaver).
See the LICENSE file in the project root for full license details.
"""
import wx
from node_editor_frame import NodeEditorFrame

if __name__ == "__main__":
    app = wx.App(False)
    NodeEditorFrame()
    app.MainLoop()
