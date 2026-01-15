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
import enum
import json
import logging
from pathlib import Path
import sys
from typing import Optional
import wx
import wx.aui
from recent_solutions_manager import RecentSolutionsManager
from recording_metadata import RecordingMetadata
from persistence.solution_persistence import SolutionPersistence, SolutionSaveStatus
from browsing.web_driver_factory import create_driver_from_solution
from browsing.studio_browser import StudioBrowser
from recording.recording_events import (
    OpenRecordingEvent,
    RenameRecordingEvent,
    DeleteRecordingEvent)
from recording.recording_session import RecordingSession
from recording_view_context import RecordingViewContext
from recording.recording_event_type import RecordingEventType
from studio_state_controller import StudioState, StudioStateController
from studio_solution import (
    StudioSolution,
    solution_load_error_to_str,
    SolutionDirectoryCreateStatus)
from solution_create_wizard.wizard_basic_info_page import WizardBasicInfoPage
from solution_create_wizard.solution_create_wizard_data import \
    SolutionCreateWizardData
from solution_create_wizard.wizard_select_browser_page import \
    WizardSelectBrowserPage
from solution_create_wizard.wizard_behaviour_page import \
    WizardBehaviourPage
from solution_create_wizard.wizard_finish_page import \
    WizardFinishPage
from solution_create_wizard.solution_creation_page import SolutionCreationPage
from solution_create_wizard.solution_widget_ids import \
    SOLUTION_WIZARD_BACK_BUTTON_ID
from ui.solution_explorer_panel import SolutionExplorerPanel
from ui.workspace_panel import WorkspacePanel
from ui.main_toolbar import MainToolbar, ToolbarState
from ui.main_menu import create_main_menu


# macOS menu bar offset
INITIAL_POSITION = wx.Point(0, 30) if sys.platform == "darwin" \
    else wx.DefaultPosition


class StatusBarElement(enum.Enum):
    """
    Enumeration of status bar field indices.

    This enum defines the logical layout of the main application status bar.
    Each value corresponds to a fixed field index in the wx status bar and
    should be used instead of hard-coded integers when updating status text.

    Fields:

        STATUS_MESSAGE (0):
            General-purpose status messages (e.g. "Ready", progress updates,
            or short-lived operation feedback).

        SOLUTION_NAME (1):
            Displays the name of the currently loaded solution, or indicates
            that no solution is loaded.

        CURRENT_MODE (2):
            Shows the current application mode and recording state
            (e.g. "Mode: Editing", "Mode: Recording ●").

        SAVE_STATUS (3):
            Indicates whether there are unsaved changes or whether all changes
            are safely saved.

        BROWSER_STATUS (4):
            Indicates whether the controlled browser instance is currently
            running or stopped.
    """
    STATUS_MESSAGE = 0
    SOLUTION_NAME = 1
    CURRENT_MODE = 2
    SAVE_STATUS = 3
    BROWSER_STATUS = 4


class StudioMainFrame(wx.Frame):
    """
    Main application window for WebWeaver Automation Studio.

    This frame is responsible for initialising the top-level user interface,
    including the menu bar, AUI-managed toolbars, and other dockable panes.
    It serves as the central coordination point for the Studio UI.
    """
    # pylint: disable=too-few-public-methods, too-many-instance-attributes

    RECENT_SOLUTION_BASE_ID: int = wx.ID_HIGHEST + 500

    SOLUTION_WIZARD_PAGE_CLASSES = {
        SolutionCreationPage.PAGE_NO_BASIC_INFO_PAGE: WizardBasicInfoPage,
        SolutionCreationPage.PAGE_NO_SELECT_BROWSER_PAGE:
            WizardSelectBrowserPage,
        SolutionCreationPage.PAGE_NO_BEHAVIOUR_PAGE: WizardBehaviourPage,
        SolutionCreationPage.PAGE_NO_FINISH_PAGE: WizardFinishPage
    }

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

        self._logger = logging.getLogger("webweaver_studio")
        self._logger.setLevel(logging.DEBUG)
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
        self._logger.addHandler(handler)

        self._toolbar = None
        """The main application toolbar (AUI-managed)."""

        self._solution_explorer_panel = None
        """Solution explorer panel part of the UI."""

        self._status_bar = None
        """Status bar part of the UI"""

        self._web_browser: Optional[StudioBrowser] = None
        """Web browser application"""

        self.recent_solutions_menu: Optional[wx.Menu] = None

        # Recording timer for capturing elements.
        self._recording_timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self._on_recording_tick, self._recording_timer)

        # Create web browser 'is alive' timer
        self._web_browser_heartbeat_timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER,
                  self._on_browser_heartbeat_tick,
                  self._web_browser_heartbeat_timer)
        # Run the heartbeat time every one second.
        self._web_browser_heartbeat_timer.Start(1000)

        self._aui_mgr: wx.aui.AuiManager = wx.aui.AuiManager(self)
        """AUI manager responsible for dockable panes and toolbars."""

        self._workspace_panel: Optional[WorkspacePanel] = None

        self._current_state: StudioState = StudioState.NO_SOLUTION
        self._recording_session: Optional[RecordingSession] = None
        self._current_solution: Optional[StudioSolution] = None
        self._state_controller: Optional[StudioStateController] = None

        self._recent_solutions: RecentSolutionsManager = RecentSolutionsManager()

        # Disable native macOS fullscreen handling
        if sys.platform == "darwin":
            self.EnableFullScreenView(False)

        # Menu Bar
        create_main_menu(self)

    @property
    def aui_manager(self) -> wx.aui.AuiManager:
        """Property Accessor for aui manager"""
        return self._aui_mgr

    @property
    def recent_solutions(self) -> RecentSolutionsManager:
        """Property Accessor for recent solutions menu"""
        return self._recent_solutions

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
        self._toolbar = MainToolbar.create(self)

        self._state_controller.ui_ready = True

        self._create_solution_panel()

        # --------------------------------------------------------------
        # Create workspace panel
        # --------------------------------------------------------------
        self._create_workspace_panel()

        self._aui_mgr.Update()

        # --------------------------------------------------------------
        # Create status bar
        # --------------------------------------------------------------
        self._create_status_bar()
        self._update_toolbar_state()

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

    def set_status_bar_status_message(self, msg: str):
        """
        Set the general-purpose status message in the status bar.

        This field is intended for short-lived feedback such as "Ready",
        progress updates, or the result of user actions.

        :param msg: The message text to display.
        """
        self._status_bar.SetStatusText(msg,
                                       StatusBarElement.STATUS_MESSAGE.value)

    def set_status_bar_current_solution(self, solution_name: Optional[str]):
        """
        Update the status bar to reflect the currently loaded solution.

        If no solution name is provided, the status bar will indicate that
        no solution is currently loaded.

        :param solution_name: The solution file name, or None if no solution
                              is loaded.
        """
        if not solution_name:
            self._status_bar.SetStatusText("No solution loaded",
                                           StatusBarElement.SOLUTION_NAME.value)
        else:
            self._status_bar.SetStatusText(f"Solution: {solution_name}",
                                           StatusBarElement.SOLUTION_NAME.value)

    def set_status_bar_mode(self, mode_name: str, is_recording: bool):
        """
        Update the status bar to show the current application mode and
        recording state.

        When recording is active, a recording indicator is appended to the
        mode text.

        :param mode_name: Human-readable name of the current mode
                          (e.g. "Editing", "Recording", "Playback").
        :param is_recording: True if a recording session is currently active.
        """
        text = f"Mode: {mode_name}"
        if is_recording:
            text += "  ● Recording"
        self._status_bar.SetStatusText(text,
                                       StatusBarElement.CURRENT_MODE.value)

    def set_status_bar_dirty(self, is_dirty: bool):
        """
        Update the status bar to reflect whether there are unsaved changes.

        :param is_dirty: True if the current solution has unsaved changes,
                         False if all changes are saved.
        """
        if is_dirty:
            self._status_bar.SetStatusText("Unsaved changes",
                                           StatusBarElement.SAVE_STATUS.value)
        else:
            self._status_bar.SetStatusText("All changes saved",
                                           StatusBarElement.SAVE_STATUS.value)

    def set_status_bar_browser_running(self, is_running: bool):
        """
        Update the status bar to reflect the current browser runtime state.

        :param is_running: True if the controlled browser instance is currently
                           running, False if it is stopped.
        """
        if is_running:
            self._status_bar.SetStatusText(
                "Browser: Running", StatusBarElement.BROWSER_STATUS.value)
        else:
            self._status_bar.SetStatusText(
                "Browser: Stopped", StatusBarElement.BROWSER_STATUS.value)

    def _on_state_changed(self, new_state):
        """
        Handle a change in the application state.

        This method updates the internally stored state and refreshes any
        UI elements (such as toolbars) that depend on the current state.

        :param new_state: The new application state object.
        """
        self._current_state = new_state
        self._update_toolbar_state()

    def on_new_solution_event(self, _event: wx.CommandEvent):
        """
        Handle the "New Solution" command and run the solution creation wizard.

        This method drives the multi-page solution creation wizard by:
          - Creating a shared SolutionCreateWizardData object
          - Displaying wizard pages in sequence
          - Handling Next, Back, and Cancel navigation
          - Creating the solution if the wizard completes successfully

        The wizard flow is controlled using the SolutionCreationPage enum and
        the SOLUTION_WIZARD_PAGE_CLASSES mapping. Each page is shown modally and
        returns a result indicating whether to proceed, go back, or cancel.

        If the user completes the final page successfully, the solution is
        created using the collected wizard data.
        """
        data: SolutionCreateWizardData = SolutionCreateWizardData()

        page_number = SolutionCreationPage.PAGE_NO_BASIC_INFO_PAGE

        while True:
            page_class = self.SOLUTION_WIZARD_PAGE_CLASSES.get(page_number)

            if not page_class:
                self._create_solution(data)
                break

            dlg = page_class(self, data)
            result = dlg.ShowModal()
            next_page = dlg.NEXT_WIZARD_PAGE
            dlg.Destroy()

            if result == SOLUTION_WIZARD_BACK_BUTTON_ID:
                # Go back, clamp to first page
                new_page: int = page_number.value - 1
                new_page = max(
                    SolutionCreationPage.PAGE_NO_BASIC_INFO_PAGE.value,
                    new_page
                )
                page_number = SolutionCreationPage(new_page)
                continue

            if result == wx.ID_OK:
                # Go forward
                page_number = next_page
                continue

            # Cancel / close / ESC
            break

    def _create_solution(self, data):
        self._current_solution = StudioSolution(
            data.solution_name,
            data.solution_directory,
            data.create_solution_dir,
            data.base_url,
            data.browser,
            data.launch_browser_automatically,
            data.browser_launch_options)

        result = SolutionPersistence.save_to_disk(self._current_solution)
        if result is not SolutionSaveStatus.OK:
            wx.MessageBox(result.value,
                          "Failed to save solution",
                          wx.ICON_ERROR,
                          self)
            return

        self._state_controller.on_solution_loaded()
        self._solution_explorer_panel.show_solution(self._current_solution)

        self._recent_solutions.add_solution(
            self._current_solution.get_solution_file_path())
        self._recent_solutions.save()

        self._rebuild_recent_solutions_menu()

        self._recording_session = RecordingSession(self._current_solution)

        # Update solution name in the status bar.
        self.set_status_bar_current_solution(
            self._current_solution.solution_name)

    def _create_status_bar(self):
        """
        Create and initialize the main application status bar.

        The status bar is divided into five fields that provide high-level,
        always-visible information about the current state of WebWeaver Studio:

            0. General status messages (e.g. "Ready", operation feedback)
            1. Currently loaded solution name
            2. Current mode and recording state (e.g. "Mode: Editing",
               "● Recording")
            3. Save state / dirty flag (e.g. "All changes saved", "Unsaved
               changes")
            4. Browser state (e.g. "Browser: Running", "Browser: Stopped")

        Each field is given a relative width so that more important contextual
        information (such as the solution name) has more space.

        This method should be called once during main frame initialization.
        """
        self._status_bar = self.CreateStatusBar(5)

        # Relative widths
        self._status_bar.SetStatusWidths([
            -2,  # General
            -3,  # Solution
            -2,  # Mode / Recording
            -1,  # Save state
            -1,  # Browser
        ])

        # Initial values
        self._status_bar.SetStatusText(
            "Ready", StatusBarElement.STATUS_MESSAGE.value)
        self._status_bar.SetStatusText("No solution loaded",
                                       StatusBarElement.SOLUTION_NAME.value)
        self._status_bar.SetStatusText("Mode: Editing",
                                       StatusBarElement.CURRENT_MODE.value)
        self._status_bar.SetStatusText("All changes saved",
                                       StatusBarElement.SAVE_STATUS.value)
        self._status_bar.SetStatusText("Browser: Stopped",
                                       StatusBarElement.BROWSER_STATUS.value)

    def on_open_solution_event(self, _event: wx.CommandEvent):
        """
        Handle the "Open Solution" command.

        Displays a file dialog allowing the user to select a Webweaver Studio
        solution file (.wws). If a solution is successfully loaded, the
        application state is updated, the solution explorer is refreshed, and a
        new recording session is initialized.
        """
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

    def on_close_solution_event(self, _event: wx.CommandEvent):
        """
        Handle the "Close Solution" command.

        Closes the currently loaded solution, resets the application state,
        and updates the UI to reflect that no solution is open.
        """
        self._current_solution = None
        self._state_controller.on_solution_closed()

        # Clear down solution explorer panel on close
        self._solution_explorer_panel.show_no_solution()

        # Clear down workspace panel on close
        self._workspace_panel.clear()

        self.set_status_bar_current_solution(None)

    def on_record_start_stop_event(self, _event: wx.CommandEvent):
        """
        Handle the toolbar/menu command to start or stop recording.

        This method toggles the recording state via the state controller and then
        performs the corresponding action:

        - If recording is being started:
            * A new recording session is created using the next available
              recording name from the current solution.
            * If starting the recording fails, an error is shown and the state
              change is reverted.

        - If recording is being stopped:
            * The active recording session is stopped.
            * If stopping the recording fails, an error is shown and the state
              change is reverted.
            * If stopping succeeds, the solution explorer is refreshed to show
              the new recording.

        Any failure during start or stop will leave the application in its
        previous state.
        """
        self._state_controller.on_record_start_stop()

        if self._state_controller.state == StudioState.RECORDING_RUNNING:
            ok = self._recording_session.start(
                self._current_solution.generate_next_recording_name())
            if not ok:
                wx.MessageBox(
                    self._recording_session.last_error or
                    "Failed to start recording.",
                    "Recording Error",
                    wx.ICON_ERROR,
                    self
                )

                # Revert state change
                self._state_controller.on_record_start_stop()
                return

            self._web_browser.enable_record_mode()
            # 100ms polling for elements
            self._recording_timer.Start(100)

        elif self._state_controller.state == StudioState.SOLUTION_LOADED:
            ok = self._recording_session.stop()
            if not ok:
                wx.MessageBox(
                    self._recording_session.last_error or
                    "Failed to stop recording.",
                    "Recording Error",
                    wx.ICON_ERROR,
                    self
                )

                # Revert state change
                self._state_controller.on_record_start_stop()
                return

            self._solution_explorer_panel.refresh_recordings(
                self._current_solution)

            self._web_browser.disable_record_mode()
            self._recording_timer.Stop()

    def on_record_pause_event(self, _event: wx.CommandEvent):
        """ Pause or resume a recording """
        self._state_controller.on_record_pause()

    def on_inspector_event(self, _event: wx.CommandEvent):
        """ PLACEHOLDER """
        if self._web_browser:
            if self._web_browser.inspect_active:
                self._web_browser.disable_inspect_mode()

            else:
                self._web_browser.enable_inspect_mode()

    def on_web_browser_event(self, _event: wx.CommandEvent):
        if not self._web_browser:
            self._web_browser = create_driver_from_solution(
                self._current_solution, self._logger)
            self._web_browser.open_page(self._current_solution.base_url)

        else:
            if self._web_browser.is_alive():
                self._web_browser.quit()
                self._web_browser = None

        self._update_toolbar_state()

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
            raw_data = SolutionPersistence.load_from_disk(solution_file)
            result = StudioSolution.from_json(raw_data)

        except (OSError, json.JSONDecodeError) as e:
            wx.MessageBox(
                f"Failed to read solution file:\n{e}",
                "Open Solution",
                wx.ICON_ERROR
            )
            return False

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

        self._web_browser = create_driver_from_solution(self._current_solution,
                                                        self._logger)
        self._web_browser.open_page(self._current_solution.base_url)

        # Update state + UI
        self._state_controller.on_solution_loaded()
        self._solution_explorer_panel.show_solution(self._current_solution)

        # Recent solutions
        self._recent_solutions.add_solution(solution_file)
        self._recent_solutions.save()
        wx.CallAfter(self.rebuild_recent_solutions_menu)

        self.set_status_bar_current_solution(self._current_solution.solution_name)

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

    def _rename_recording_event(self, _evt: wx.CommandEvent) -> None:
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

        self._workspace_panel.on_recording_renamed_by_id(recording.id,
                                                         new_name)
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

    def rebuild_recent_solutions_menu(self) -> None:
        """
        Rebuild the "Recent Solutions" menu from the current recent solutions list.
        """

        # Remove all existing items
        while self.recent_solutions_menu.GetMenuItemCount() > 0:
            item = self.recent_solutions_menu.FindItemByPosition(0)
            self.recent_solutions_menu.Delete(item)

        menu_id = self.RECENT_SOLUTION_BASE_ID

        for path in self._recent_solutions.get_solutions():
            self.recent_solutions_menu.Append(menu_id, str(path))

            self.Bind(
                wx.EVT_MENU,
                self._on_open_recent_solution_event,
                id=menu_id
            )

            menu_id += 1

        if self.recent_solutions_menu.GetMenuItemCount() == 0:
            item = self.recent_solutions_menu.Append(
                self.RECENT_SOLUTION_BASE_ID, "(empty)")
            item.Enable(False)

    def _on_open_recent_solution_event(self, evt: wx.CommandEvent) -> None:
        """
        Handle selection of an entry from the "Recent Solutions" menu.

        The menu item ID is mapped back to an index in the recent solutions list.
        The selected solution is opened, and a new recording session is created
        for the newly opened solution.
        """
        index: int = evt.GetId() - self.RECENT_SOLUTION_BASE_ID
        self._open_solution(self._recent_solutions.get_solutions()[index])

        self._recording_session = RecordingSession(
            self._current_solution)

    def _update_toolbar_state(self) -> None:
        """
        Recompute and apply the toolbar UI state based on the current studio state.

        This method translates the application's logical state (e.g. no solution,
        solution loaded, recording, paused, inspecting) into a ToolbarState model
        and applies it to the main toolbar.

        All toolbar buttons are first reset to a disabled state, then selectively
        enabled and updated according to the current StudioState. Browser-related
        toolbar state is updated separately.
        """
        # First: disable everything that is state-dependent
        MainToolbar.set_all_disabled(self._toolbar)

        state = ToolbarState()

        # Only New/Open make sense
        if self._current_state == StudioState.NO_SOLUTION:
            pass

        elif self._current_state == StudioState.SOLUTION_LOADED:
            state = ToolbarState(can_save=True, can_close=True,
                                 can_inspect=True, can_record=True,
                                 can_browse=True)

        elif self._current_state == StudioState.RECORDING_RUNNING:
            state = ToolbarState(can_record=True, can_pause=True, is_recording=True)

        elif self._current_state == StudioState.RECORDING_PAUSED:
            state = ToolbarState(can_record=True, can_pause=True,
                                 is_recording=True, is_paused=True)

        elif self._current_state == StudioState.INSPECTING:
            state = ToolbarState(can_save=True, can_close=True,
                                 can_record=True, can_inspect=True)

        MainToolbar.apply_state(self._toolbar, state)
        self._manage_browser_state()

    def _on_browser_heartbeat_tick(self, _event):
        """
        Periodic timer callback used to detect if the browser has been closed externally.

        If a browser instance exists but is no longer alive, this method treats it
        as having been closed by the user and triggers the appropriate cleanup and
        UI updates.
        """
        if self._web_browser and not self._web_browser.is_alive():
            self._on_browser_closed_by_user()

    def _on_browser_closed_by_user(self):
        """
        Handle the case where the browser was closed outside of the application.

        Clears the internal browser reference, notifies the user, and updates the
        UI to reflect that no browser is currently running.
        """
        self._web_browser = None

        wx.MessageBox(
            "The browser was closed.",
            "Browser Closed",
            wx.ICON_INFORMATION
        )

        self._manage_browser_state()

    def _manage_browser_state(self):
        """
        Synchronize the UI with the current browser running state.

        This method checks whether a browser instance exists and is alive, updates
        the status bar indicator, and updates the toolbar browser toggle button to
        reflect the current state.
        """
        if not self._web_browser:
            state = False
        else:
            state = self._web_browser.is_alive()

        self.set_status_bar_browser_running(state)

        MainToolbar.manage_browser_status(self._toolbar, state)

    def _on_recording_tick(self, _evt):
        if not self._recording_session or not self._recording_session.is_recording():
            return

        if not self._web_browser:
            return

        self._web_browser.poll()
        events = self._web_browser.pop_recorded_events()

        for ev in events:
            # For now, just store raw events
            self._recording_session.append_event(
                RecordingEventType.DOM_CLICK,
                payload=ev
            )
