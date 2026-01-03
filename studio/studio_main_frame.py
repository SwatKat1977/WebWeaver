"""
This source file is part of Web Weaver
For the latest info, see https://github.com/SwatKat1977/WebWeaver

Copyright 2025 SwatKat1977

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
import sys
from typing import Optional
import wx
import wx.aui
# from solution_explorer_panel import SolutionExplorerPanel
from toolbar_icons import (
    load_toolbar_inspect_icon,
    load_toolbar_new_solution_icon,
    load_toolbar_open_solution_icon,
    load_toolbar_pause_record_icon,
    load_toolbar_save_solution_icon,
    load_toolbar_start_record_icon,
    # load_toolbar_stop_record_icon,
    # load_toolbar_resume_record_icon,
    load_toolbar_close_solution_icon)

# macOS menu bar offset
INITIAL_POSITION = wx.Point(0, 30) if sys.platform == "darwin" \
    else wx.DefaultPosition


class StudioMainFrame(wx.Frame):
    """
    Main application window for WebWeaver Automation Studio.

    This frame is responsible for initialising the top-level user interface,
    including the menu bar, AUI-managed toolbars, and other dockable panes.
    It serves as the central coordination point for the Studio UI.
    """
    # pylint: disable=too-few-public-methods

    TOOLBAR_ID_NEW_SOLUTION: int = wx.ID_HIGHEST + 1
    """Toolbar command ID for creating a new solution."""

    TOOLBAR_ID_OPEN_SOLUTION: int = wx.ID_HIGHEST + 2
    """Toolbar command ID for opening an existing solution."""

    TOOLBAR_ID_SAVE_SOLUTION: int = wx.ID_HIGHEST + 3
    """Toolbar command ID for saving the current solution."""

    TOOLBAR_ID_CLOSE_SOLUTION: int = wx.ID_HIGHEST + 4
    """Toolbar command ID for closing the current solution."""

    TOOLBAR_ID_INSPECTOR_MODE: int = wx.ID_HIGHEST + 5
    """Toolbar command ID for toggling Inspector mode."""

    TOOLBAR_ID_START_STOP_RECORD: int = wx.ID_HIGHEST + 6
    """Toolbar command ID for starting or stopping recording."""

    TOOLBAR_ID_PAUSE_RECORD: int = wx.ID_HIGHEST + 7
    """Toolbar command ID for pausing an active recording."""

    def __init__(self, parent: Optional[wx.Window] = None):
        """
        Initialise the main application frame.

        This sets up the frame window, menu bar, and platform-specific
        behaviour. AUI-managed components are initialised separately
        via :meth:`init_aui`.
        """
        super().__init__(
            parent,
            title="Webweaver Automation Studio",
            pos=INITIAL_POSITION,
            size=wx.Size(1024, 768),
            style=wx.DEFAULT_FRAME_STYLE,
        )

        self._toolbar = None
        """The main application toolbar (AUI-managed)."""

        self._aui_mgr: wx.aui.AuiManager = wx.aui.AuiManager()
        """AUI manager responsible for dockable panes and toolbars."""

        # Disable native macOS fullscreen handling
        if sys.platform == "darwin":
            self.EnableFullScreenView(False)

        # --------------------------------------------------------------
        # Menu Bar
        # --------------------------------------------------------------
        menubar = wx.MenuBar()

        # -- File Menu --
        file_menu = wx.Menu()
        file_menu.Append(wx.ID_NEW, "New Project\tCtrl+N")
        file_menu.Append(wx.ID_OPEN, "Open Project\tCtrl+O")

        self._recent_solutions_menu = wx.Menu()
        file_menu.AppendSubMenu(self._recent_solutions_menu,
                                "Recent Solutions")

        file_menu.Append(wx.ID_SAVE, "Save Project\tCtrl+S")
        file_menu.AppendSeparator()
        file_menu.Append(wx.ID_EXIT, "Exit\tCtrl-X")
        menubar.Append(file_menu, "File")
        self.SetMenuBar(menubar)

        # Help menu (actual help items only)
        help_menu = wx.Menu()
        help_menu.Append(wx.ID_ANY, "WebWeaver Help")
        help_menu.Append(wx.ID_ABOUT, "About WebWeaver")
        menubar.Append(help_menu, "Help")

        self.SetMenuBar(menubar)

    def init_aui(self) -> None:
        """
        Initialise AUI-managed components for the frame.

        This method attaches the AUI manager to the frame, resets any
        previously stored layout, applies visual metrics, and creates
        the main toolbar.
        """
        self._aui_mgr.SetManagedWindow(self)

        # Reset any previously stored layout
        self._aui_mgr.LoadPerspective("", True)

        self._aui_mgr.GetArtProvider().SetMetric(wx.aui.AUI_DOCKART_SASH_SIZE,
                                                2)

        # --------------------------------------------------------------
        # TOOLBAR (top, dockable)
        # --------------------------------------------------------------
        self._create_main_toolbar()

    def _create_main_toolbar(self):
        """
        Create and configure the main application toolbar.

        The toolbar is docked at the top of the frame and contains
        commands for solution management, inspection mode, and
        recording control.
        """
        self._toolbar = wx.aui.AuiToolBar(
            self,
            wx.ID_ANY,
            wx.DefaultPosition,
            wx.DefaultSize,
            wx.NO_BORDER
            | wx.aui.AUI_TB_DEFAULT_STYLE
            | wx.aui.AUI_TB_TEXT
            | wx.aui.AUI_TB_HORZ_LAYOUT)

        self._toolbar.SetToolBitmapSize(wx.Size(32, 32))
        self._toolbar.SetToolPacking(5)
        self._toolbar.SetToolSeparation(5)

        self._toolbar.AddTool(
            self.TOOLBAR_ID_NEW_SOLUTION,
            "",
            load_toolbar_new_solution_icon(),
            "Create New Solution",)

        self._toolbar.AddTool(
            self.TOOLBAR_ID_OPEN_SOLUTION,
            "",
            load_toolbar_open_solution_icon(),
            "Open Solution")

        self._toolbar.AddTool(
            self.TOOLBAR_ID_SAVE_SOLUTION,
            "",
            load_toolbar_save_solution_icon(),
            "Save Solution")

        self._toolbar.AddTool(
            self.TOOLBAR_ID_CLOSE_SOLUTION,
            "",
            load_toolbar_close_solution_icon(),
            "Close Solution")

        self._toolbar.AddSeparator()

        self._toolbar.AddTool(
            self.TOOLBAR_ID_INSPECTOR_MODE,
            "",
            load_toolbar_inspect_icon(),
            "Inspector Mode",
            wx.ITEM_CHECK)

        self._toolbar.AddTool(
            self.TOOLBAR_ID_START_STOP_RECORD,
            "",
            load_toolbar_start_record_icon(),
            "Record")

        self._toolbar.AddTool(
            self.TOOLBAR_ID_PAUSE_RECORD,
            "",
            load_toolbar_pause_record_icon(),
            "Pause Recording")

        self._toolbar.Realize()

        # --- Bind toolbar events ---
        self._toolbar.Bind(
            wx.EVT_TOOL,
            self.on_new_solution_event,
            id=self.TOOLBAR_ID_NEW_SOLUTION)

        self._toolbar.Bind(
            wx.EVT_TOOL,
            self.on_close_solution_event,
            id=self.TOOLBAR_ID_CLOSE_SOLUTION)

        self._toolbar.Bind(
            wx.EVT_TOOL,
            self.on_open_solution_event,
            id=self.TOOLBAR_ID_OPEN_SOLUTION)

        self._toolbar.Bind(
            wx.EVT_TOOL,
            self.on_record_start_stop_event,
            id=self.TOOLBAR_ID_START_STOP_RECORD)

        self._toolbar.Bind(
            wx.EVT_TOOL,
            self.on_record_pause_event,
            id=self.TOOLBAR_ID_PAUSE_RECORD)

        self._toolbar.Bind(
            wx.EVT_TOOL,
            self.on_inspector_event,
            id=self.TOOLBAR_ID_INSPECTOR_MODE)

        self._aui_mgr.AddPane(
            self._toolbar,
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

        self._aui_mgr.Update()

    def on_new_solution_event(self, _event: wx.CommandEvent):
        ...

    def on_close_solution_event(self, _event: wx.CommandEvent):
        ...

    def on_open_solution_event(self, _event: wx.CommandEvent):
        ...

    def on_record_start_stop_event(self, _event: wx.CommandEvent):
        ...

    def on_record_pause_event(self, _event: wx.CommandEvent):
        ...

    def on_inspector_event(self, _event: wx.CommandEvent):
        ...
