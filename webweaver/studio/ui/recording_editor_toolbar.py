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
from webweaver.studio.recording_toolbar_icons import (
                                       load_toolbar_add_step_icon,
                                       load_toolbar_edit_step_icon,
                                       load_toolbar_delete_step_icon,
                                       load_toolbar_move_step_up_icon,
                                       load_toolbar_move_step_down_icon)
# pylint: disable=duplicate-code


class RecordingToolbarId:
    """
    Command ID constants for the Recording Editor (Steps) toolbar.

    These IDs are used for wx command events emitted by the toolbar buttons
    and reposted to the main application frame. The frame or higher-level
    controllers can then handle the commands in a centralized and
    state-aware manner.

    The IDs are intentionally defined in a single namespace to avoid
    collisions and to make it explicit which commands belong to the
    recording editor toolbar.
    """
    # pylint: disable=too-few-public-methods

    #: Command ID for adding a new step.
    ADD_STEP = wx.ID_HIGHEST + 6001

    #: Command ID for deleting the currently selected step.
    STEP_DELETE = wx.ID_HIGHEST + 6002

    #: Command ID for editing the currently selected step.
    STEP_EDIT = wx.ID_HIGHEST + 6003

    #: Command ID for moving the selected step down in the timeline.
    MOVE_STEP_DOWN = wx.ID_HIGHEST + 6004

    #: Command ID for moving the selected step up in the timeline.
    MOVE_STEP_UP = wx.ID_HIGHEST + 6005


@dataclass(frozen=True)
class RecordingEditorToolbarState:
    """
    Immutable UI state model for the recording editor (steps) toolbar.

    This value object represents which editing actions are currently
    permitted based on application state (e.g. whether a step is selected,
    whether it can be moved, etc.).

    Instances of this class are typically produced by higher-level UI or
    state controllers and applied to the toolbar via
    RecordingEditorToolbar.apply_state().

    Being immutable allows cheap equality comparison to avoid unnecessary
    UI updates.
    """

    #: Whether the selected step can be moved up.
    can_move_up: bool = False

    #: Whether the selected step can be moved down.
    can_move_down: bool = False

    #: Whether the selected step can be edited.
    can_edit: bool = False

    #: Whether the selected step can be deleted.
    can_delete: bool = False


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
    Instead, it emits command events (e.g. RecordingToolbarId.STEP_DELETE) to the
    main frame, where higher-level controllers decide how to apply the
    requested action to the active recording and UI.
    """

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
        self._last_state: RecordingEditorToolbarState | None = None

        def _bundle(bmp: wx.Bitmap) -> wx.BitmapBundle:
            # wxPython Phoenix expects BitmapBundle in many tool APIs
            return wx.BitmapBundle.FromBitmap(bmp)

        bmp_add = load_toolbar_add_step_icon()
        bmp_up = load_toolbar_move_step_up_icon()
        bmp_down = load_toolbar_move_step_down_icon()
        bmp_edit = load_toolbar_edit_step_icon()
        bmp_delete = load_toolbar_delete_step_icon()

        self._toolbar = wx.aui.AuiToolBar(
            frame,
            style=wx.aui.AUI_TB_DEFAULT_STYLE | wx.aui.AUI_TB_HORIZONTAL)

        self._toolbar.AddTool(
            RecordingToolbarId.ADD_STEP,
            "",
            _bundle(bmp_add),
            "Add Step")

        self._toolbar.AddTool(
            RecordingToolbarId.MOVE_STEP_UP,
            "",
            _bundle(bmp_up),
            "Move Step Up")

        self._toolbar.AddTool(
            RecordingToolbarId.MOVE_STEP_DOWN,
            "",
            _bundle(bmp_down),
            "Move Step Down")

        self._toolbar.AddTool(
            RecordingToolbarId.STEP_EDIT,
            "",
            _bundle(bmp_edit),
            "Edit Step")

        self._toolbar.AddTool(
            RecordingToolbarId.STEP_DELETE,
            "",
            _bundle(bmp_delete),
            "Delete Step")

        self._toolbar.Bind(wx.EVT_TOOL, self._on_delete, id=RecordingToolbarId.STEP_DELETE)
        self._toolbar.Bind(wx.EVT_TOOL, self._on_edit, id=RecordingToolbarId.STEP_EDIT)

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

    def apply_state(self, state: RecordingEditorToolbarState) -> None:
        """
        Apply a RecordingEditorToolbarState model to the toolbar.

        This method enables or disables toolbar buttons according to the
        provided state object. If the state has not changed since the last
        application, no UI update is performed.

        The toolbar window is temporarily frozen during updates to avoid
        flicker and unnecessary redraws.
        """
        if state == self._last_state:
            return  # <-- nothing changed, no repaint

        self._last_state = state

        tb = self._toolbar

        pane = self._aui_mgr.GetPane("StepsToolbar")
        win = pane.window if pane.IsOk() else self._toolbar
        win.Freeze()

        try:
            tb.EnableTool(RecordingToolbarId.STEP_DELETE, state.can_delete)
            tb.EnableTool(RecordingToolbarId.STEP_EDIT, state.can_edit)
            tb.EnableTool(RecordingToolbarId.MOVE_STEP_DOWN, state.can_move_down)
            tb.EnableTool(RecordingToolbarId.MOVE_STEP_UP, state.can_move_up)

            # Usually not strictly needed, but safe:
            tb.Refresh()
        finally:
            win.Thaw()

    def _on_delete(self, _evt):
        """
        Handle the Delete Step toolbar button.

        This method reposts a RecordingToolbarId.STEP_DELETE command event to the
        main frame so the active recording controller can perform the deletion
        in a centralized, state-aware, and undo-safe manner.
        """
        wx.PostEvent(
            self._frame,
            wx.CommandEvent(wx.EVT_TOOL.typeId, RecordingToolbarId.STEP_DELETE))

    def _on_edit(self, _evt):
        """
        Handle the Edit Step toolbar button.

        This method reposts a RecordingToolbarId.STEP_EDIT command event to the
        main frame so the active recording controller can open the step editor
        and apply any changes in a centralized and state-aware manner.
        """
        wx.PostEvent(
            self._frame,
            wx.CommandEvent(wx.EVT_TOOL.typeId, RecordingToolbarId.STEP_EDIT))
