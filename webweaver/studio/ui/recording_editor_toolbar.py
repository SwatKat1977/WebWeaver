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
from recording_toolbar_icons import (load_toolbar_edit_step_icon,
                                     load_toolbar_delete_step_icon,
                                     load_toolbar_move_step_up_icon,
                                     load_toolbar_move_step_down_icon)

TOOLBAR_ID_STEP_DELETE = wx.ID_HIGHEST + 6001
"""
Toolbar command ID for deleting the currently selected recording step.

This ID is emitted by the RecordingEditorToolbar and reposted to the main
frame so higher-level controllers can handle step deletion in a central,
state-aware way.
"""


class RecordingEditorToolbar:
    """
    Toolbar providing editing actions for a recording's step timeline.

    This toolbar is shown alongside the recording editor and exposes
    step-level operations such as:

        - Move step up
        - Move step down
        - Edit step
        - Delete step

    The toolbar itself does not perform the editing operations directly.
    Instead, it emits command events (e.g. TOOLBAR_ID_STEP_DELETE) to the
    main frame, where higher-level controllers decide how to apply the
    requested action to the active recording and UI.
    """
    # pylint: disable=too-few-public-methods

    def __init__(self, frame: wx.Frame, aui_mgr: wx.aui.AuiManager):
        """
        Create and register the recording editor steps toolbar.

        The toolbar is added to the AUI manager as a docked toolbar pane
        and is hidden by default. It is typically shown only when a
        recording is open and active.

        :param frame: The main application frame that will receive reposted
                      toolbar command events.
        :param aui_mgr: The AUI manager responsible for docking and layout.
        """
        self._frame = frame
        self._aui_mgr = aui_mgr

        self._toolbar = wx.aui.AuiToolBar(
            frame,
            style=wx.aui.AUI_TB_DEFAULT_STYLE | wx.aui.AUI_TB_HORIZONTAL
        )

        self._toolbar.AddTool(
            wx.ID_ANY,
            "",
            load_toolbar_move_step_up_icon(),
            "Move Step Up")

        self._toolbar.AddTool(
            wx.ID_ANY,
            "",
            load_toolbar_move_step_down_icon(),
            "Move Step Down")

        self._toolbar.AddTool(
            wx.ID_ANY,
            "",
            load_toolbar_edit_step_icon(),
            "Edit Step")

        self._toolbar.AddTool(
            TOOLBAR_ID_STEP_DELETE,
            "",
            load_toolbar_delete_step_icon(),
            "Delete Step")

        self._toolbar.Bind(wx.EVT_TOOL, self._on_delete, id=TOOLBAR_ID_STEP_DELETE)

        self._toolbar.Realize()

        self._aui_mgr.AddPane(
            self._toolbar,
            wx.aui.AuiPaneInfo()
                .Name("StepsToolbar")
                .Caption("Steps")
                .ToolbarPane()
                .Top()
                .Row(2)
                .DockFixed(True)
                .Hide())

    @property
    def toolbar(self):
        """
        Return the underlying wx AUI toolbar widget.

        This is primarily used by the main frame or layout controller to
        show/hide the toolbar or query its state.
        """
        return self._toolbar

    def _on_delete(self, _evt):
        """
        Handle the Delete Step toolbar button.

        This method reposts a TOOLBAR_ID_STEP_DELETE command event to the
        main frame so the active recording controller can perform the
        deletion in a centralized and state-aware manner.
        """
        wx.PostEvent(
            self._frame,
            wx.CommandEvent(wx.EVT_TOOL.typeId, TOOLBAR_ID_STEP_DELETE))
