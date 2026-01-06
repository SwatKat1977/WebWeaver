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
import json
from pathlib import Path
import sys
from typing import Optional
import wx
import wx.aui
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
from workspace_panel import WorkspacePanel
from solution_explorer_panel import SolutionExplorerPanel
from recording.recording_events import (
    OpenRecordingEvent,
    RenameRecordingEvent,
    DeleteRecordingEvent)
from recording_metadata import RecordingMetadata
from recording.recording_session import RecordingSession
from recording_view_context import RecordingViewContext
from studio_state_controller import StudioState, StudioStateController
from studio_solution import (
    StudioSolution,
    solution_load_error_to_str,
    SolutionDirectoryCreateStatus)

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

        self._solution_explorer_panel = None

        self._aui_mgr: wx.aui.AuiManager = wx.aui.AuiManager(self)
        """AUI manager responsible for dockable panes and toolbars."""

        self._workspace_panel: Optional[WorkspacePanel] = None

        self._current_state_: StudioState = StudioState.NO_SOLUTION
        self._recording_session: Optional[RecordingSession] = None
        self._current_solution: Optional[StudioSolution] = None
        self._state_controller: Optional[StudioStateController] = None

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

        self._aui_mgr.GetArtProvider().SetMetric(
            wx.aui.AUI_DOCKART_SASH_SIZE,
            2)

        self._state_controller = StudioStateController(self._on_state_changed)

        # --------------------------------------------------------------
        # TOOLBAR (top, dockable)
        # --------------------------------------------------------------
        self._create_main_toolbar()

        self._state_controller.ui_ready = True

        self._create_solution_panel()

        # --------------------------------------------------------------
        # Create workspace panel
        # --------------------------------------------------------------
        self._create_workspace_panel()

        self._aui_mgr.Update()

        # --------------------------------------------------------------
        # Recordings events
        # --------------------------------------------------------------

        # Open recording event.
        self.Bind(OpenRecordingEvent, self._open_recording_event)

        # Delete recording event.
        self.Bind(DeleteRecordingEvent, self._delete_recording_event)

        # Rename recording event.
        self.Bind(RenameRecordingEvent, self._rename_recording_event)

        # Force wxAUI to compute sizes/paint.
        self.Layout()
        self.SendSizeEvent()

        wx.CallLater(1, self._aui_mgr.Update)
        wx.CallLater(1, self.SendSizeEvent)

    def _on_state_changed(self, new_state):
        self.current_state = new_state
        #self.update_toolbar_state()

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

    def on_new_solution_event(self, _event: wx.CommandEvent):
        ...

    def on_close_solution_event(self, _event: wx.CommandEvent):
        ...

    def on_open_solution_event(self, _event: wx.CommandEvent):
        dlg: wx.FileDialog = wx.FileDialog(
            self,
            message="Open Webweaver Studio solution",
            defaultDir="",
            defaultFile="",
            wildcard="Webweaver Solution (*.wws)|*.wws",
            style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)

        try:
            if dlg.ShowModal() == wx.ID_OK:
                path = Path(dlg.GetPath())

                if self._open_solution(path):
                    self._state_controller.on_solution_loaded()
                    self._solution_explorer_panel.show_solution(
                        self._current_solution
                    )

                    self._recording_session = RecordingSession(
                        self._current_solution)

        finally:
            dlg.Destroy()

    def on_record_start_stop_event(self, _event: wx.CommandEvent):
        ...

    def on_record_pause_event(self, _event: wx.CommandEvent):
        ...

    def on_inspector_event(self, _event: wx.CommandEvent):
        ...

    def _create_solution_panel(self) -> None:
        # Solution panel (left top)
        self._solution_explorer_panel = SolutionExplorerPanel(self)

        self._aui_mgr.AddPane(self._solution_explorer_panel,
                        wx.aui.AuiPaneInfo()
                        .Left()
                        .Row(1)
                        .PaneBorder(False)
                        .Caption("Solution Explorer")
                        .CloseButton(True)
                        .MaximizeButton(True)
                        .MinimizeButton(True)
                        .BestSize(300, 300))

    def _create_workspace_panel(self):
        # -------------------------
        # Workspace
        # -------------------------
        self._workspace_panel = WorkspacePanel(self)

        info = (
            wx.aui.AuiPaneInfo()
            .Name("Workspace")
            .CenterPane()
            .PaneBorder(False)
            .CaptionVisible(False)
            .Show(True)
        )

        self._aui_mgr.AddPane(self._workspace_panel, info)

        self._workspace_panel.Show(True)
        self._aui_mgr.GetPane("Workspace").Show(True)

    def _open_solution(self, solution_file: Path) -> bool:
        if not solution_file.exists():
            wx.MessageBox(
                "Solution file does not exist.",
                "Open Solution",
                wx.ICON_ERROR
            )
            return False

        try:
            with solution_file.open("r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            wx.MessageBox(
                f"Failed to read solution file:\n{e}",
                "Open Solution",
                wx.ICON_ERROR
            )
            return False

        # Load solution from JSON
        result = StudioSolution.from_json(data)

        if result.solution is None:
            wx.MessageBox(
                solution_load_error_to_str(result.error),
                "Open Solution",
                wx.ICON_ERROR
            )
            return False

        self._current_solution = result.solution

        # Ensure directory structure (safe, idempotent)
        status = self._current_solution.ensure_directory_structure()
        if status != SolutionDirectoryCreateStatus.NONE_:
            wx.MessageBox(
                "Failed to prepare solution folders.",
                "Open Solution",
                wx.ICON_ERROR
            )
            self._current_solution = None
            return False

        # Update state + UI
        self._state_controller.on_solution_loaded()
        self._solution_explorer_panel.show_solution(self._current_solution)

        # Recent solutions
        #self.recent_solutions.add_solution(solution_file)
        #self.recent_solutions.save()
        #self.rebuild_recent_solutions_menu()

        return True

    def _open_recording_event(self, evt: wx.CommandEvent) -> None:
        metadata = evt.GetClientData()
        if not metadata or not self._current_solution or \
                not self._workspace_panel:
            return

        # 1. Ask the solution for a view context
        ctx: RecordingViewContext = self._current_solution.open_recording(
            metadata)

        # 2. Tell the workspace to display it
        self._workspace_panel.open_recording(ctx)

    def _rename_recording_event(self, evt: wx.CommandEvent) -> None:
        if self._state_controller.state in (StudioState.RECORDING_RUNNING,
                                            StudioState.RECORDING_PAUSED):
            wx.MessageBox(
                "Stop recording before renaming recordings.",
                "Rename Recording",
                wx.ICON_WARNING,
                self)
            return

        recording = self._solution_explorer_panel.get_selected_recording()

        dlg: wx.TextEntryDialog = wx.TextEntryDialog(
            self,
            "Enter a new name for the recording:",
            "Rename Recording",
            recording.name)

        if dlg.ShowModal() != wx.ID_OK:
            return

        new_name: str = dlg.GetValue()

        if not new_name:
            return

        # Make a copy of the recording to update.
        updated: RecordingMetadata = recording
        updated.name = new_name

        if not updated.update_recording_name():
            wx.MessageBox(
                "Failed to save recording metadata.",
                "Rename Recording",
                wx.ICON_ERROR,
                self)
            return

        #workspacePanel_->OnRecordingRenamedById(recording->id, newName);
        self._solution_explorer_panel.refresh_recordings(self._current_solution)

    def _delete_recording_event(self, evt: wx.CommandEvent) -> None:
        if self._state_controller.state in (StudioState.RECORDING_RUNNING,
                                            StudioState.RECORDING_PAUSED):
            wx.MessageBox(
                "You cannot delete recordings while a recording session is "
                "active.\n\nStop the recording first.",
                "Delete Recording",
                wx.ICON_WARNING,
                self)
            return

        path = Path(evt.GetClientData())
        if not path or not self._current_solution:
            return

        filename = Path(path).name
        rc: int = wx.MessageBox(
            f"Delete recording?\n\n{filename}",
            "Delete Recording",
            wx.YES_NO | wx.ICON_WARNING,
            self)
        if rc is not wx.YES:
            return

        try:
            Path(path).unlink()
        except OSError as e:
            wx.MessageBox(
                f"Failed to delete recording:\n{e}",
                "Delete Recording",
                wx.ICON_ERROR,
                self
            )
            return

        selected = self._solution_explorer_panel.get_selected_recording()
        selected_id = selected.id if selected else ""

        if selected_id:
            self._workspace_panel.on_recording_deleted_by_id(selected_id)

        self._solution_explorer_panel.refresh_recordings(self._current_solution)
