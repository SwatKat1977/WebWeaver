"""
This source file is part of Web Weaver
For the latest info, see https://github.com/SwatKat1977/WebWeaver

Copyright 2025-2026 Webweaver Development Team

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
import wx
import wx.aui
from toolbar_icons import (
    load_toolbar_inspect_icon,
    load_toolbar_new_solution_icon,
    load_toolbar_open_solution_icon,
    load_toolbar_pause_record_icon,
    load_toolbar_save_solution_icon,
    load_toolbar_start_record_icon,
    load_toolbar_close_solution_icon,
    load_toolbar_web_browser_icon)


def create_main_toolbar(frame: "StudioMainFrame") -> wx.aui.AuiToolBar:
    """
    Create and configure the main application toolbar.

    The toolbar is docked at the top of the frame and contains
    commands for solution management, inspection mode, and
    recording control.
    """
    toolbar = wx.aui.AuiToolBar(
        frame,
        wx.ID_ANY,
        wx.DefaultPosition,
        wx.DefaultSize,
        wx.NO_BORDER
        | wx.aui.AUI_TB_DEFAULT_STYLE
        | wx.aui.AUI_TB_TEXT
        | wx.aui.AUI_TB_HORZ_LAYOUT)

    toolbar.SetToolBitmapSize(wx.Size(32, 32))
    toolbar.SetToolPacking(5)
    toolbar.SetToolSeparation(5)

    toolbar.AddTool(
        frame.TOOLBAR_ID_NEW_SOLUTION,
        "",
        load_toolbar_new_solution_icon(),
        "Create New Solution")

    toolbar.AddTool(
        frame.TOOLBAR_ID_OPEN_SOLUTION,
        "",
        load_toolbar_open_solution_icon(),
        "Open Solution")

    toolbar.AddTool(
        frame.TOOLBAR_ID_SAVE_SOLUTION,
        "",
        load_toolbar_save_solution_icon(),
        "Save Solution")

    toolbar.AddTool(
        frame.TOOLBAR_ID_CLOSE_SOLUTION,
        "",
        load_toolbar_close_solution_icon(),
        "Close Solution")

    toolbar.AddSeparator()

    toolbar.AddTool(
        frame.TOOLBAR_ID_INSPECTOR_MODE,
        "",
        load_toolbar_inspect_icon(),
        "Inspector Mode",
        wx.ITEM_CHECK)

    toolbar.AddTool(
        frame.TOOLBAR_ID_START_STOP_RECORD,
        "",
        load_toolbar_start_record_icon(),
        "Record")

    toolbar.AddTool(
        frame.TOOLBAR_ID_PAUSE_RECORD,
        "",
        load_toolbar_pause_record_icon(),
        "Pause Recording")

    toolbar.AddTool(
        frame.TOOLBAR_ID_WEB_BROWSER,
        "",
        load_toolbar_web_browser_icon(),
        "Open Web Browser",
        wx.ITEM_CHECK)

    toolbar.Realize()

    # --- Bind toolbar events ---
    toolbar.Bind(
        wx.EVT_TOOL,
        frame.on_new_solution_event,
        id=frame.TOOLBAR_ID_NEW_SOLUTION)

    toolbar.Bind(
        wx.EVT_TOOL,
        frame.on_close_solution_event,
        id=frame.TOOLBAR_ID_CLOSE_SOLUTION)

    toolbar.Bind(
        wx.EVT_TOOL,
        frame.on_open_solution_event,
        id=frame.TOOLBAR_ID_OPEN_SOLUTION)

    toolbar.Bind(
        wx.EVT_TOOL,
        frame.on_record_start_stop_event,
        id=frame.TOOLBAR_ID_START_STOP_RECORD)

    toolbar.Bind(
        wx.EVT_TOOL,
        frame.on_record_pause_event,
        id=frame.TOOLBAR_ID_PAUSE_RECORD)

    toolbar.Bind(
        wx.EVT_TOOL,
        frame.on_inspector_event,
        id=frame.TOOLBAR_ID_INSPECTOR_MODE)

    frame.aui_manager.AddPane(
        toolbar,
        wx.aui.AuiPaneInfo()
        .Name("MainToolbar")
        .ToolbarPane()
        .Top()
        .Row(0)
        .Position(0)
        .LeftDockable(False)
        .RightDockable(False)
        .BottomDockable(False)
        .Gripper(False)
        .Floatable(False)
        .Movable(False))

    return toolbar
