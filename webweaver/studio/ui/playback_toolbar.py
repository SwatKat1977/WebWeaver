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
from dataclasses import dataclass
from ui.playback_toolbar_icons import (
    load_playback_toolbar_pause_icon,
    load_playback_toolbar_play_icon,
    load_playback_toolbar_step_icon,
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
        return self._toolbar

    def _create_controls(self):
        self._btn_play = self._toolbar.AddTool(TOOLBAR_ID_START_PLAYBACK,
                                               "Play",
                                               load_playback_toolbar_play_icon(),
                                               kind=wx.ITEM_NORMAL)
        self._btn_pause = self._toolbar.AddTool(TOOLBAR_ID_PAUSE_PLAYBACK,
                                                "Pause",
                                                load_playback_toolbar_pause_icon(),
                                                kind=wx.ITEM_NORMAL)
        self._btn_stop = self._toolbar.AddTool(TOOLBAR_ID_STOP_PLAYBACK,
                                               "Stop",
                                               load_playback_toolbar_stop_icon(),
                                               kind=wx.ITEM_NORMAL)

        """ This is a future feature """
        # self._btn_step = self._toolbar.AddTool(
        #    TOOLBAR_ID_STEP_PLAYBACK, "Step", PlaybackIcons.STEP, kind=wx.ITEM_NORMAL)

        self._toolbar.Bind(wx.EVT_TOOL, self._on_play, self._btn_play)
        self._toolbar.Bind(wx.EVT_TOOL, self._on_pause, self._btn_pause)
        self._toolbar.Bind(wx.EVT_TOOL, self._on_stop, self._btn_stop)
        # self._toolbar.Bind(wx.EVT_TOOL, self._on_step, self._btn_step)

    # Event handlers (PLACEHOLDERS FOR NOW)
    def _on_play(self, _evt): pass
    def _on_pause(self, _evt): pass
    def _on_stop(self, _evt): pass
    def _on_step(self, _evt): pass

    @staticmethod
    def set_all_disabled(toolbar: wx.aui.AuiToolBar):
        for tool in toolbar.GetTools():
            toolbar.EnableTool(tool.GetId(), False)

    @staticmethod
    def apply_state(toolbar: "PlaybackToolbar", state: PlaybackToolbarState):
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
