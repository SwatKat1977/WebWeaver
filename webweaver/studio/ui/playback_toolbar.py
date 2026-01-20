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
from ui.playback_toolbar_icons import (
    load_playback_toolbar_pause_icon,
    load_playback_toolbar_play_icon,
    # load_playback_toolbar_step_icon,   FUTURE FEATURE
    load_playback_toolbar_stop_icon)


TOOLBAR_ID_START_PLAYBACK: int = wx.ID_HIGHEST + 2001
"""Toolbar command ID for starting playback."""

TOOLBAR_ID_PAUSE_PLAYBACK: int = wx.ID_HIGHEST + 2002
"""Toolbar command ID for pausing playback."""

TOOLBAR_ID_STOP_PLAYBACK: int = wx.ID_HIGHEST + 2003
"""Toolbar command ID for stopping playback."""

TOOLBAR_ID_STEP_PLAYBACK: int = wx.ID_HIGHEST + 2004
"""Toolbar command ID for stepping playback."""


@dataclass(slots=True)
class PlaybackToolbarState:
    """
    Declarative UI state model for the playback toolbar.

    This dataclass describes which playback controls should be enabled and what
    the current execution state is. It is produced by the studio state controller
    (or main frame) and applied to the PlaybackToolbar to update the UI.

    Fields
    ------
    can_play : bool
        Whether the Play button should be enabled.
    can_pause : bool
        Whether the Pause button should be enabled.
    can_stop : bool
        Whether the Stop button should be enabled.
    can_step : bool
        Whether the Step button should be enabled (future feature).
    is_running : bool
        Whether playback is currently running.
    is_paused : bool
        Whether playback is currently paused.
    """
    can_play: bool = False
    can_pause: bool = False
    can_stop: bool = False
    can_step: bool = False
    is_running: bool = False
    is_paused: bool = False


class PlaybackToolbar:
    """
    Secondary toolbar that provides controls for recording playback.

    This toolbar is only visible while the studio is in any playback-related
    state. It exposes transport-style controls such as play, pause, stop, and
    step, and reflects the current playback state via enabled/disabled buttons
    and toggle states.
    """

    def __init__(self, frame: wx.Frame, aui_mgr: wx.aui.AuiManager):
        """
        Create the playback toolbar and register it with the AUI manager.

        The toolbar is created hidden by default and is shown or hidden by the
        main frame depending on the current studio state.

        :param frame: The main application frame.
        :param aui_mgr: The AUI manager responsible for layout and docking.
        """
        self._frame = frame
        self._aui_mgr = aui_mgr

        self._toolbar = wx.aui.AuiToolBar(
            frame,
            style=wx.aui.AUI_TB_DEFAULT_STYLE | wx.aui.AUI_TB_HORIZONTAL
        )

        self._create_controls()
        self._toolbar.Realize()

        self._aui_mgr.AddPane(
            self._toolbar,
            wx.aui.AuiPaneInfo()
                .Name("PlaybackToolbar")
                .Caption("Playback")
                .ToolbarPane()
                .Top()
                .Row(1)          # <-- second row
                .DockFixed(True)
                .Hide()
        )

    @property
    def toolbar(self) -> wx.aui.AuiToolBar:
        """
        Get the underlying wx AUI toolbar instance.

        This is primarily used by the main frame or layout manager when applying
        state or manipulating the AUI pane.
        """
        return self._toolbar

    def _create_controls(self):
        """
        Create and bind all toolbar controls.

        This method populates the toolbar with the playback transport buttons
        (play, pause, stop). Additional controls such as step may be added in
        the future.
        """
        self._btn_play = self._toolbar.AddTool(TOOLBAR_ID_START_PLAYBACK,
                                               "",
                                               load_playback_toolbar_play_icon(),
                                               "Start Playback")
        self._btn_pause = self._toolbar.AddTool(TOOLBAR_ID_PAUSE_PLAYBACK,
                                                "",
                                                load_playback_toolbar_pause_icon(),
                                                "Pause Playback")
        self._btn_stop = self._toolbar.AddTool(TOOLBAR_ID_STOP_PLAYBACK,
                                               "",
                                               load_playback_toolbar_stop_icon(),
                                               "Stop Playback")

        # --- This is a future feature ---
        # self._btn_step = self._toolbar.AddTool(
        #    TOOLBAR_ID_STEP_PLAYBACK, "Step", PlaybackIcons.STEP, kind=wx.ITEM_NORMAL)

        self._toolbar.Bind(wx.EVT_TOOL, self._on_play, self._btn_play)
        self._toolbar.Bind(wx.EVT_TOOL, self._on_pause, self._btn_pause)
        self._toolbar.Bind(wx.EVT_TOOL, self._on_stop, self._btn_stop)
        # self._toolbar.Bind(wx.EVT_TOOL, self._on_step, self._btn_step)

    # Event handlers (PLACEHOLDERS FOR NOW)
    def _on_play(self, _evt):
        """
        Handle the Play button being pressed.

        This will eventually start or resume playback via the playback controller.
        """

    def _on_pause(self, _evt):
        """
        Handle the Pause button being pressed.

        This will eventually pause playback via the playback controller.
        """

    def _on_stop(self, _evt):
        """
        Handle the Stop button being pressed.

        This will eventually stop playback and return to the idle playback state.
        """

    def _on_step(self, _evt):
        """
        Handle the Step button being pressed.

        This is a future feature that will advance playback by a single step.
        """

    @staticmethod
    def set_all_disabled(toolbar: wx.aui.AuiToolBar):
        """
        Disable all tools in the given toolbar.

        This is used as the first step when applying a new PlaybackToolbarState,
        after which only the appropriate buttons are re-enabled.
        """
        for tool in toolbar.GetTools():
            toolbar.EnableTool(tool.GetId(), False)

    @staticmethod
    def apply_state(toolbar: "PlaybackToolbar", state: PlaybackToolbarState):
        """
        Apply a PlaybackToolbarState to the given PlaybackToolbar.

        This method updates the enabled/disabled state of all playback controls
        to reflect the provided declarative state model.

        :param toolbar: The PlaybackToolbar instance to update.
        :param state: The desired UI state for the playback toolbar.
        """
        PlaybackToolbar.set_all_disabled(toolbar.toolbar)

        if state.can_play:
            toolbar.toolbar.EnableTool(TOOLBAR_ID_START_PLAYBACK, True)

        if state.can_pause:
            toolbar.toolbar.EnableTool(TOOLBAR_ID_PAUSE_PLAYBACK, True)

        if state.can_stop:
            toolbar.toolbar.EnableTool(TOOLBAR_ID_STOP_PLAYBACK, True)

        if state.can_step:
            toolbar.toolbar.EnableTool(TOOLBAR_ID_STEP_PLAYBACK, True)

        toolbar.toolbar.Realize()
