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
from dataclasses import dataclass
import wx
import wx.aui
from webweaver.studio.toolbar_icons import (
    load_toolbar_inspect_icon,
    load_toolbar_new_solution_icon,
    load_toolbar_open_solution_icon,
    load_toolbar_pause_record_icon,
    load_toolbar_resume_record_icon,
    load_toolbar_close_solution_icon,
    load_toolbar_web_browser_icon,
    load_toolbar_start_record_icon,
    load_toolbar_stop_record_icon,
    load_toolbar_add_step_icon,
    load_toolbar_edit_step_icon,
    load_toolbar_delete_step_icon)
from .playback_toolbar_icons import (
    load_playback_toolbar_pause_icon,
    load_playback_toolbar_play_icon,
    # load_playback_toolbar_step_icon,   FUTURE FEATURE
    load_playback_toolbar_stop_icon)


TOOLBAR_ID_NEW_SOLUTION: int = wx.ID_HIGHEST + 1
"""Toolbar command ID for creating a new solution."""

TOOLBAR_ID_OPEN_SOLUTION: int = wx.ID_HIGHEST + 2
"""Toolbar command ID for opening an existing solution."""

TOOLBAR_ID_CLOSE_SOLUTION: int = wx.ID_HIGHEST + 3
"""Toolbar command ID for closing the current solution."""

TOOLBAR_ID_INSPECTOR_MODE: int = wx.ID_HIGHEST + 4
"""Toolbar command ID for toggling Inspector mode."""

TOOLBAR_ID_START_STOP_RECORD: int = wx.ID_HIGHEST + 5
"""Toolbar command ID for starting or stopping recording."""

TOOLBAR_ID_PAUSE_RECORD: int = wx.ID_HIGHEST + 6
"""Toolbar command ID for pausing an active recording."""

TOOLBAR_ID_WEB_BROWSER: int = wx.ID_HIGHEST + 7
"""Toolbar command ID for web browser control."""

TOOLBAR_ID_PLAYBACK_START_STOP: int = wx.ID_HIGHEST + 8
"""Toolbar command ID for starting/stopping playback."""

TOOLBAR_ID_PLAYBACK_PAUSE: int = wx.ID_HIGHEST + 9
"""Toolbar command ID for pausing playback."""

TOOLBAR_ID_PLAYBACK_STEP: int = wx.ID_HIGHEST + 10
"""Toolbar command ID for stepping playback."""

TOOLBAR_ID_RECORDING_ADD_STEP: int = wx.ID_HIGHEST + 11
"""Toolbar command ID for adding a recording step."""

TOOLBAR_ID_RECORDING_DELETE_STEP: int = wx.ID_HIGHEST + 12
"""Toolbar command ID for deleting a recording step."""

TOOLBAR_ID_RECORDING_EDIT_STEP: int = wx.ID_HIGHEST + 13
"""Toolbar command ID for editing a recording step."""


@dataclass(frozen=True)
class ToolbarState:
    """
    Apply a ToolbarState model to the given toolbar.

    This method updates:
    - Which buttons are enabled or disabled
    - The appearance and tooltip of the recording and pause buttons
    - The checked state of the inspector toggle

    The toolbar is re-realized and refreshed after all changes are applied.
    """
    # pylint: disable=too-many-instance-attributes

    # Main functionality
    can_close: bool = False
    can_inspect: bool = False
    can_record: bool = False
    can_pause: bool = False
    can_browse: bool = False
    is_recording: bool = False
    is_recording_paused: bool = False
    is_inspecting: bool = False
    browser_running: bool = False

    # Playback functionality
    can_start_playback: bool = False
    can_stop_playback: bool = False
    can_pause_playback: bool = False
    can_step_playback: bool = False
    is_playback_running: bool = False
    is_playback_paused: bool = False

    # Recording functionality
    can_add_recording_step: bool = False
    can_edit_recording_step: bool = False
    can_delete_recording_step: bool = False


class MainToolbar:
    """
    Helper class for creating and updating the main application toolbar.

    This class is a namespace-style container for toolbar construction and
    rendering logic. It does not hold state; it only operates on wx toolbars.
    """

    @staticmethod
    def create(frame: "StudioMainFrame") -> wx.aui.AuiToolBar:
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
        toolbar.SetToolPacking(6)
        toolbar.SetToolSeparation(8)

        toolbar.AddTool(
            TOOLBAR_ID_NEW_SOLUTION,
            "",
            load_toolbar_new_solution_icon(),
            "Create New Solution")

        toolbar.AddTool(
            TOOLBAR_ID_OPEN_SOLUTION,
            "",
            load_toolbar_open_solution_icon(),
            "Open Solution")

        toolbar.AddTool(
            TOOLBAR_ID_CLOSE_SOLUTION,
            "",
            load_toolbar_close_solution_icon(),
            "Close Solution")

        # --- Recording Group ---
        toolbar.AddSeparator()

        toolbar.AddTool(
            TOOLBAR_ID_START_STOP_RECORD,
            "",
            load_toolbar_start_record_icon(),
            "Record")

        toolbar.AddTool(
            TOOLBAR_ID_PAUSE_RECORD,
            "",
            load_toolbar_pause_record_icon(),
            "Pause Recording")

        # --- Browser-Related Group ---
        toolbar.AddSeparator()

        toolbar.AddTool(
            TOOLBAR_ID_WEB_BROWSER,
            "",
            load_toolbar_web_browser_icon(),
            "Open Web Browser",
            wx.ITEM_CHECK)

        toolbar.AddTool(
            TOOLBAR_ID_INSPECTOR_MODE,
            "",
            load_toolbar_inspect_icon(),
            "Inspector Mode",
            wx.ITEM_CHECK)

        # --- Playback Group ---
        toolbar.AddSeparator()

        toolbar.AddTool(
            TOOLBAR_ID_PLAYBACK_START_STOP,
            "",
            load_playback_toolbar_play_icon(),
            "Start Playback")

        toolbar.AddTool(
            TOOLBAR_ID_PLAYBACK_PAUSE,
            "",
            load_playback_toolbar_pause_icon(),
            "Pause Playback",
            wx.ITEM_CHECK)

        # --- Recordings Group ---
        toolbar.AddSeparator()

        toolbar.AddTool(
            TOOLBAR_ID_RECORDING_ADD_STEP,
            "",
            load_toolbar_add_step_icon(),
            "Add Step")

        toolbar.AddTool(
            TOOLBAR_ID_RECORDING_EDIT_STEP,
            "",
            load_toolbar_edit_step_icon(),
            "Edit Step")

        toolbar.AddTool(
            TOOLBAR_ID_RECORDING_DELETE_STEP,
            "",
            load_toolbar_delete_step_icon(),
            "Delete Step")

        toolbar.Realize()

        # --- Bind core toolbar events ---
        toolbar.Bind(wx.EVT_TOOL,
                     frame.on_new_solution_event,
                     id=TOOLBAR_ID_NEW_SOLUTION)

        toolbar.Bind(wx.EVT_TOOL,
                     frame.on_close_solution_event,
                     id=TOOLBAR_ID_CLOSE_SOLUTION)

        toolbar.Bind(wx.EVT_TOOL,
                     frame.on_open_solution_event,
                     id=TOOLBAR_ID_OPEN_SOLUTION)

        toolbar.Bind(wx.EVT_TOOL,
                     frame.on_record_start_stop_event,
                     id=TOOLBAR_ID_START_STOP_RECORD)

        toolbar.Bind(wx.EVT_TOOL,
                     frame.on_record_pause_event,
                     id=TOOLBAR_ID_PAUSE_RECORD)

        toolbar.Bind(wx.EVT_TOOL,
                     frame.on_inspector_event,
                     id=TOOLBAR_ID_INSPECTOR_MODE)

        toolbar.Bind(wx.EVT_TOOL,
                     frame.on_web_browser_event,
                     id=TOOLBAR_ID_WEB_BROWSER)

        # --- Bind recording playback toolbar events ---
        toolbar.Bind(wx.EVT_TOOL,
                     frame.on_recording_playback_start_stop,
                     id=TOOLBAR_ID_PLAYBACK_START_STOP)
        toolbar.Bind(wx.EVT_TOOL,
                     frame.on_pause_recording_playback,
                     id=TOOLBAR_ID_PLAYBACK_PAUSE)

        # --- Bind recording playback editing events ---
        toolbar.Bind(wx.EVT_TOOL,
                     frame.on_recording_step_add,
                     id=TOOLBAR_ID_RECORDING_ADD_STEP)
        toolbar.Bind(wx.EVT_TOOL,
                     frame.on_recording_step_delete,
                     id=TOOLBAR_ID_RECORDING_DELETE_STEP)
        toolbar.Bind(wx.EVT_TOOL,
                     frame.on_recording_step_edit,
                     id=TOOLBAR_ID_RECORDING_EDIT_STEP)

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

    @staticmethod
    def apply_state(toolbar: wx.aui.AuiToolBar,
                    toolbar_state: ToolbarState) -> None:
        """
        Apply a ToolbarState model to the given toolbar.

        This method updates:
        - Which buttons are enabled or disabled
        - The appearance and tooltip of the recording and pause buttons
        - The checked state of the inspector toggle

        The toolbar is re-realized and refreshed after all changes are applied.
        """

        # Enable / disable
        toolbar.EnableTool(TOOLBAR_ID_CLOSE_SOLUTION, toolbar_state.can_close)
        toolbar.EnableTool(TOOLBAR_ID_INSPECTOR_MODE,
                           toolbar_state.can_inspect)
        toolbar.EnableTool(TOOLBAR_ID_START_STOP_RECORD,
                           toolbar_state.can_record)
        toolbar.EnableTool(TOOLBAR_ID_PAUSE_RECORD, toolbar_state.can_pause)
        toolbar.EnableTool(TOOLBAR_ID_WEB_BROWSER, toolbar_state.can_browse)

        # Recording button appearance
        if toolbar_state.is_recording:
            toolbar.SetToolBitmap(TOOLBAR_ID_START_STOP_RECORD,
                                  load_toolbar_stop_record_icon())
            toolbar.SetToolShortHelp(TOOLBAR_ID_START_STOP_RECORD,
                                     "Stop Recording")
        else:
            toolbar.SetToolBitmap(TOOLBAR_ID_START_STOP_RECORD,
                                  load_toolbar_start_record_icon())
            toolbar.SetToolShortHelp(TOOLBAR_ID_START_STOP_RECORD,
                                     "Start Recording")

        # Pause recording button appearance
        if toolbar_state.is_recording_paused:
            toolbar.SetToolBitmap(TOOLBAR_ID_PAUSE_RECORD,
                                  load_toolbar_resume_record_icon())
            toolbar.SetToolShortHelp(TOOLBAR_ID_PAUSE_RECORD,
                                     "Resume Recording")
        else:
            toolbar.SetToolBitmap(TOOLBAR_ID_PAUSE_RECORD,
                                  load_toolbar_pause_record_icon())
            toolbar.SetToolShortHelp(TOOLBAR_ID_PAUSE_RECORD,
                                     "Pause Recording")

        # Playback Enable / disable
        MainToolbar.set_playback_start_stop_button(
            toolbar, toolbar_state.is_playback_running)
        toolbar.EnableTool(TOOLBAR_ID_PLAYBACK_START_STOP,
                           toolbar_state.can_start_playback)
        toolbar.EnableTool(TOOLBAR_ID_PLAYBACK_PAUSE,
                           toolbar_state.can_pause_playback)
        #    toolbar.EnableTool(PlaybackToolID.TOOLBAR_ID_STEP_PLAYBACK,
        #                       playback_state.can_step)

        # Inspector toggle
        toolbar.ToggleTool(TOOLBAR_ID_INSPECTOR_MODE,
                           toolbar_state.is_inspecting)

        # Recording enable/disable
        toolbar.EnableTool(TOOLBAR_ID_RECORDING_ADD_STEP,
                           toolbar_state.can_add_recording_step)
        toolbar.EnableTool(TOOLBAR_ID_RECORDING_EDIT_STEP,
                           toolbar_state.can_edit_recording_step)
        toolbar.EnableTool(TOOLBAR_ID_RECORDING_DELETE_STEP,
                           toolbar_state.can_delete_recording_step)

        toolbar.Realize()
        toolbar.Refresh()

    @staticmethod
    def set_playback_start_stop_button(toolbar: wx.aui.AuiToolBar,
                                       started: bool):
        """Updates the playback start/stop toolbar button.

        Changes the toolbar button icon and tooltip depending on whether
        playback is currently running.

        Args:
            toolbar (wx.aui.AuiToolBar): The toolbar containing the playback
                start/stop tool.
            started (bool): True if playback has started and the button should
                display the "Stop" icon and tooltip. False if playback is not
                running and the button should display the "Start" icon and
                tooltip.
        """
        if started:
            toolbar.SetToolBitmap(TOOLBAR_ID_PLAYBACK_START_STOP,
                                  load_playback_toolbar_stop_icon())
            toolbar.SetToolShortHelp(TOOLBAR_ID_PLAYBACK_START_STOP,
                                     "Stop Playback")
        else:
            toolbar.SetToolBitmap(TOOLBAR_ID_PLAYBACK_START_STOP,
                                  load_playback_toolbar_play_icon())
            toolbar.SetToolShortHelp(TOOLBAR_ID_PLAYBACK_START_STOP,
                                     "Start Playback")

    @staticmethod
    def manage_browser_status(toolbar: wx.aui.AuiToolBar, state: bool) -> None:
        """
        Update the browser toggle button to reflect the current browser state.

        This sets both the checked state and tooltip of the browser button to
        indicate whether the browser is currently running or not.
        """
        toolbar.ToggleTool(TOOLBAR_ID_WEB_BROWSER, state)

        toolbar.SetToolShortHelp(
            TOOLBAR_ID_WEB_BROWSER,
            "Close Web Browser" if state else "Open Web Browser")

        toolbar.Realize()
        toolbar.Refresh()
