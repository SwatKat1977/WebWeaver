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
# pylint: disable=too-many-lines
import json
import logging
from pathlib import Path
import sys
from typing import Optional
from selenium.common.exceptions import (WebDriverException,
                                        InvalidSessionIdException)
import wx
import wx.aui
from recent_solutions_manager import RecentSolutionsManager
from recording_metadata import RecordingMetadata
from persistence.solution_persistence import (SolutionPersistence,
                                              SolutionSaveStatus)
from persistence.recording_document import RecordingDocument
from persistence.recording_persistence import RecordingPersistence
from browsing.web_driver_factory import create_driver_from_solution
from browsing.studio_browser import StudioBrowser
from recording_view_context import RecordingViewContext
from recording.recording_events import (
    OpenRecordingEvent,
    RenameRecordingEvent,
    DeleteRecordingEvent)
from recording.recording_session import RecordingSession
from recording.recording_event_type import RecordingEventType
from recording.recording_loader import load_recording_from_context
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
from ui.main_status_bar import MainStatusBar
from ui.inspector_panel import InspectorPanel
from ui.playback_toolbar import (PlaybackToolbarState,
                                 PlaybackToolbar,
                                 PlaybackToolID)
from ui.recording_editor_toolbar import (RecordingEditorToolbar,
                                         RecordingEditorToolbarState,
                                         RecordingToolbarId)
from ui.events import EVT_WORKSPACE_ACTIVE_CHANGED
from playback.recording_playback_session import RecordingPlaybackSession
from code_generation.code_generator_registry import CodeGeneratorRegistry


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
            style=wx.DEFAULT_FRAME_STYLE)

        self._logger = logging.getLogger("webweaver_studio")
        self._logger.setLevel(logging.DEBUG)
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
        self._logger.addHandler(handler)
        self._pending_recording_toolbar_update = False

        self._toolbar = None
        """The main application toolbar (AUI-managed)."""

        self._solution_explorer_panel = None
        """Solution explorer panel part of the UI."""

        self._status_bar = None
        """Status bar part of the UI"""

        self._web_browser: Optional[StudioBrowser] = None
        """Web browser application"""

        self._inspector_panel: Optional[wx.Panel] = None

        self.recent_solutions_menu: Optional[wx.Menu] = None
        self.code_generation_menu: Optional[wx.Menu] = None

        self._playback_toolbar: Optional[PlaybackToolbar] = None

        plugin_path: str = "webweaver/studio/code_generator_plugins"
        self._code_gen_registry = CodeGeneratorRegistry(Path(plugin_path),
                                                        self._logger)
        self._code_gen_registry.load()

        # --------------------------------------------------------------
        # Recording Playback Parameters
        # --------------------------------------------------------------
        self._playback_session: Optional[RecordingPlaybackSession] = None
        self._playback_timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self._on_playback_timer, self._playback_timer)

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

        # Create web browser 'inspect' timer
        self._inspector_timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self._on_inspector_timer, self._inspector_timer)
        self._inspector_timer.Start(200)

        self._aui_mgr: wx.aui.AuiManager = wx.aui.AuiManager(self)
        """AUI manager responsible for dockable panes and toolbars."""

        self._workspace_panel: Optional[WorkspacePanel] = None

        self._current_state: StudioState = StudioState.NO_SOLUTION
        self._recording_session: Optional[RecordingSession] = None
        self._current_solution: Optional[StudioSolution] = None
        self._state_controller: Optional[StudioStateController] = None
        self._recording_toolbar: Optional[RecordingEditorToolbar] = None

        self._recent_solutions: RecentSolutionsManager = RecentSolutionsManager()

        # Disable native macOS fullscreen handling
        if sys.platform == "darwin":
            self.EnableFullScreenView(False)

        # Menu Bar
        create_main_menu(self)

        self.Bind(wx.EVT_CLOSE, self._on_close_app)

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
        self._recording_toolbar = RecordingEditorToolbar(self, self._aui_mgr)

        self.Bind(wx.EVT_TOOL,
                  self._on_recording_step_edit,
                  id=RecordingToolbarId.STEP_EDIT)
        self.Bind(wx.EVT_TOOL,
                  self._on_recording_step_delete,
                  id=RecordingToolbarId.STEP_DELETE)

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
        self._status_bar = MainStatusBar(self)
        self._update_toolbar_state()

        self._create_inspector_panel()

        self._playback_toolbar = PlaybackToolbar(self, self._aui_mgr)

        # --------------------------------------------------------------
        # Recordings events
        # --------------------------------------------------------------

        # Open recording event.
        self.Bind(OpenRecordingEvent, self._open_recording_event)

        # Delete recording event.
        self.Bind(DeleteRecordingEvent, self._delete_recording_event)

        # Rename recording event.
        self.Bind(RenameRecordingEvent, self._rename_recording_event)

        self.Bind(EVT_WORKSPACE_ACTIVE_CHANGED,
                  self._on_workspace_active_changed)

        # --------------------------------------------------------------
        # Recording playback events
        # --------------------------------------------------------------
        self.Bind(wx.EVT_TOOL,
                  self._on_start_recording_playback,
                  id=PlaybackToolID.START_PLAYBACK)
        self.Bind(wx.EVT_TOOL,
                  self._on_pause_recording_playback,
                  id=PlaybackToolID.PAUSE_PLAYBACK)
        self.Bind(wx.EVT_TOOL,
                  self._on_stop_recording_playback,
                  id=PlaybackToolID.STOP_PLAYBACK)

        # Force wxAUI to compute sizes/paint.
        self.Layout()
        self.SendSizeEvent()

        wx.CallLater(1, self._aui_mgr.Update)
        wx.CallLater(1, self.SendSizeEvent)

    def rebuild_code_generation_menu(self) -> None:
        """
        Rebuild the Code Generation menu from the currently registered
        generators.

        This method fully clears and repopulates the code generation menu based
        on the contents of the CodeGeneratorRegistry.

        Behaviour:
            - All existing menu items are removed.
            - If no generators are registered, a single disabled placeholder
              item "(No generators found)" is shown.
            - If generators exist:
                - One menu item is created per generator.
                - Menu items are enabled only if a recording is currently
                  active.
                - Each menu item is bound to invoke code generation for its
                  corresponding generator.

        The enabled/disabled state reflects whether code generation is currently
        possible (i.e. a recording document is loaded).

        This method should be called whenever:
            - The set of available generators changes
            - The active recording document changes
            - The UI needs to be resynchronized with application state
        """
        # Remove all existing items
        while self.code_generation_menu.GetMenuItemCount() > 0:
            item = self.code_generation_menu.FindItemByPosition(0)
            self.code_generation_menu.Delete(item)

        generators = self._code_gen_registry.get_generators()

        if not generators:
            item = self.code_generation_menu.Append(wx.ID_ANY,
                                                    "(No generators found)")
            item.Enable(False)
        else:
            has_recording = self.get_active_recording_document() is not None

            for gen in generators:
                item = self.code_generation_menu.Append(wx.ID_ANY, gen.name)
                item.Enable(has_recording)
                self.Bind(
                    wx.EVT_MENU,
                    lambda evt, g=gen: self._on_generate_code(g),
                    item)

    def _on_generate_code(self, generator):
        doc = self.get_active_recording_document()
        if not doc:
            wx.MessageBox("No active recording.", "Generate Code")
            return

        code = generator.generate(doc)

        with wx.FileDialog(
                self,
                "Save generated test",
                wildcard="Python files (*.py)|*.py|All files (*.*)|*.*",
                style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT,
        ) as dlg:
            if dlg.ShowModal() != wx.ID_OK:
                return

            path = dlg.GetPath()

        with open(path, "w", encoding="utf-8") as f:
            f.write(code)

        wx.MessageBox(f"Test generated successfully:\n{path}", "Generate Code")

    def get_active_recording_document(self) -> RecordingDocument | None:
        """
        Return the RecordingDocument for the currently active workspace page.

        This method queries the workspace for the active viewer and, if it
        represents a recording-backed view, loads and returns the corresponding
        RecordingDocument from disk.

        This method returns None if:
            - The workspace panel does not exist
            - There is no active viewer page
            - The active page does not represent a recording

        The returned document represents the authoritative, file-backed state of
        the recording and should be treated as immutable by callers.

        :return: The active RecordingDocument, or None if no recording is active.
        """
        if not self._workspace_panel:
            return None

        page = self._workspace_panel.get_active_viewer()
        if not page:
            return None

        return RecordingPersistence.load_from_disk(page.get_recording_file())

    def on_refresh_codegen_generators(self, _evt):
        """
        Reload all code generator plugins and rebuild the Code Generation menu.

        This handler forces the CodeGeneratorRegistry to rescan and reload all
        available generator plugins, then refreshes the UI menu to reflect the
        updated set.

        This is typically invoked by a UI command such as:
            - "Reload Code Generators"
            - A developer/debug menu action
            - Or a plugin refresh command during development
        """
        self._code_gen_registry.load()
        self.rebuild_code_generation_menu()

    def _on_state_changed(self, new_state):
        """
        Handle a change in the application state.

        This method updates the internally stored state and refreshes any
        UI elements (such as toolbars) that depend on the current state.

        :param new_state: The new application state object.
        """
        self._current_state = new_state
        self._update_toolbar_state()
        self._update_playback_toolbar_state()

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

        self.rebuild_recent_solutions_menu()

        self._recording_session = RecordingSession(self._current_solution)

        # Update solution name in the status bar.
        self._status_bar.set_status_bar_current_solution(
            self._current_solution.solution_name)

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

        self._status_bar.set_status_bar_current_solution(None)

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
        """
        Handle the Record/Pause toolbar or menu action.

        This toggles the recording state via the central state controller.
        Depending on the current state, this will either:

        - Pause an active recording session, or
        - Resume a paused recording session

        The actual state transition logic is owned by the state controller;
        this method only forwards the user intent.
        """
        self._state_controller.on_record_pause()

    def on_inspector_event(self, _event: wx.CommandEvent):
        """
        Handle the Inspect Mode toggle action.

        This enables or disables DOM inspection mode in the active browser
        session. When inspection mode is enabled, user clicks in the browser
        are intercepted and element metadata is captured instead of being
        treated as normal interactions.

        If no browser is currently active, this action has no effect.
        """
        if self._web_browser:
            if self._web_browser.inspect_active:
                self._web_browser.disable_inspect_mode()
                self._state_controller.on_inspector_toggle(False)
                self._show_inspector_panel(False)

            else:
                self._web_browser.enable_inspect_mode()
                self._state_controller.on_inspector_toggle(True)
                self._show_inspector_panel(True)

    def on_playback_mode_event(self, _event: wx.CommandEvent):
        """
        Handle the user toggling playback mode from the main toolbar.

        This method acts as a mode switch between normal editing mode and
        playback mode:

        - If the studio is not currently in any playback state, playback mode
          is entered by transitioning to RECORDING_PLAYBACK_IDLE.
        - If the studio is already in a playback state, playback mode is exited
          and the studio returns to the SOLUTION_LOADED state.

        The visibility of the playback toolbar is also updated to match the new
        mode.
        """
        in_playback = self._current_state in {
            StudioState.RECORDING_PLAYBACK_IDLE,
            StudioState.RECORDING_PLAYBACK_RUNNING,
            StudioState.RECORDING_PLAYBACK_PAUSED}

        if not in_playback:
            self._state_controller.on_recording_playback_idle()
        else:
            self._state_controller.on_solution_loaded()

        self._show_playback_toolbar(not in_playback)

    def _show_playback_toolbar(self, show: bool) -> None:
        """
        Show or hide the playback toolbar pane.

        This method controls the visibility of the secondary playback toolbar
        managed by the AUI layout system. Callers should not manipulate the
        AUI pane directly.

        :param show: True to show the playback toolbar, False to hide it.
        """
        pane = self._aui_mgr.GetPane("PlaybackToolbar")

        if not pane.IsOk():
            print("PlaybackToolbar pane not found in AUI manager")
            #wx.LogWarning("PlaybackToolbar pane not found in AUI manager")
            return

        pane.Show(show)

        self._aui_mgr.Update()

    def on_web_browser_event(self, _event: wx.CommandEvent):
        """
        Handle the Start/Stop Browser action.

        This toggles the lifecycle of the integrated web browser:

        - If no browser is currently running, a new WebDriver instance is
          created from the current solution configuration and navigated to
          the solution's base URL.

        - If a browser is already running and still alive, it is shut down
          and the session is destroyed.

        After changing the browser state, the toolbar UI is updated to
        reflect the new state.
        """
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

        if self._current_solution.launch_browser_automatically:
            self._web_browser = create_driver_from_solution(
                self._current_solution, self._logger)
            self._web_browser.open_page(self._current_solution.base_url)

        # Update state + UI
        self._state_controller.on_solution_loaded()
        self._solution_explorer_panel.show_solution(self._current_solution)

        # Recent solutions
        self._recent_solutions.add_solution(solution_file)
        self._recent_solutions.save()
        wx.CallAfter(self.rebuild_recent_solutions_menu)

        self._status_bar.set_status_bar_current_solution(
            self._current_solution.solution_name)

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

    def _update_playback_toolbar_state(self):

        PlaybackToolbar.set_all_disabled(self._playback_toolbar)

        # Hide unless in playback
        in_playback = self._current_state in {
            StudioState.RECORDING_PLAYBACK_IDLE,
            StudioState.RECORDING_PLAYBACK_RUNNING,
            StudioState.RECORDING_PLAYBACK_PAUSED,
        }

        self._aui_mgr.GetPane("PlaybackToolbar").Show(in_playback)

        state = PlaybackToolbarState()

        if self._current_state == StudioState.RECORDING_PLAYBACK_IDLE:
            state = PlaybackToolbarState(can_play=True,
                                         can_step=False,
                                         can_stop=False)

        elif self._current_state == StudioState.RECORDING_PLAYBACK_RUNNING:
            state = PlaybackToolbarState(can_pause=True,
                                         can_stop=True,
                                         is_running=True)

        elif self._current_state == StudioState.RECORDING_PLAYBACK_PAUSED:
            state = PlaybackToolbarState(can_play=True,
                                         can_step=True,
                                         can_stop=True,
                                         is_paused=True)

        PlaybackToolbar.apply_state(self._playback_toolbar, state)
        self._aui_mgr.Update()

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

        has_recording = self._workspace_panel.has_active_recording()

        # Only New/Open make sense
        if self._current_state == StudioState.NO_SOLUTION:
            pass

        elif self._current_state == StudioState.SOLUTION_LOADED:
            browser_is_alive = self._web_browser is not None and \
                self._web_browser.is_alive()

            state = ToolbarState(can_save=True, can_close=True,
                                 can_inspect=browser_is_alive,
                                 can_record=browser_is_alive,
                                 can_browse=True,
                                 can_playback_recording=has_recording)

        elif self._current_state == StudioState.RECORDING_RUNNING:
            state = ToolbarState(can_record=True, can_pause=True,
                                 is_recording=True)

        elif self._current_state == StudioState.RECORDING_PAUSED:
            state = ToolbarState(can_record=True, can_pause=True,
                                 is_recording=True, is_paused=True)

        elif self._current_state == StudioState.INSPECTING:
            state = ToolbarState(can_save=True, can_close=True,
                                 can_record=True, can_inspect=True)

        elif self._current_state == StudioState.RECORDING_PLAYBACK_IDLE:
            state = ToolbarState(can_save=True, can_close=True,
                                 can_playback_recording=True)

        elif self._current_state == StudioState.RECORDING_PLAYBACK_RUNNING:
            pass

        elif self._current_state == StudioState.RECORDING_PLAYBACK_PAUSED:
            state = ToolbarState(can_playback_recording=has_recording)

        MainToolbar.apply_state(self._toolbar, state)
        self._manage_browser_state()

    def _update_recording_toolbar_state(self) -> None:
        if not self._workspace_panel.has_active_recording():
            self._recording_toolbar.apply_state(RecordingEditorToolbarState())
            return

        page = self._workspace_panel.get_active_viewer()
        if not page:
            self._recording_toolbar.apply_state(RecordingEditorToolbarState())
            return

        step_index = page.selected_step
        step_count = page.step_count
        has_selection = step_index is not None

        state: RecordingEditorToolbarState = RecordingEditorToolbarState()

        if has_selection:
            move_up = step_index > 0
            move_down = step_index < step_count - 1
            state = RecordingEditorToolbarState(can_edit=True,
                                                can_delete=True,
                                                can_move_up=move_up,
                                                can_move_down=move_down)

        self._recording_toolbar.apply_state(state)

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
        if self._web_browser is None:
            return  # Already closed/handled

        self._web_browser = None

        was_recording: bool = (
                self._recording_session and
                self._recording_session.is_recording())

        if was_recording:
            self._recording_session.stop()
            # force state back
            self._state_controller.on_record_start_stop()

        # If 'inspecting' and the browser is closed then make sure we
        # cleanly drop out of inspecting.
        if self._state_controller.state == StudioState.INSPECTING:
            self._show_inspector_panel(False)
            self._state_controller.on_solution_loaded()

        self._manage_browser_state()
        self._update_toolbar_state()

    def _handle_browser_died(self, reason: str | None = None):
        """
        Handle the case where the browser was closed, crashed, or the WebDriver
        session became invalid.

        This method is safe to call multiple times.
        """
        if self._web_browser is None:
            return  # Already handled

        self._logger.warning("Browser session lost. Reason: %s", reason)

        # Reuse your existing shutdown logic
        self._on_browser_closed_by_user()

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

        self._status_bar.set_status_bar_browser_running(state)

        MainToolbar.manage_browser_status(self._toolbar, state)

    def _on_recording_tick(self, _evt):
        if not self._recording_session or not self._recording_session.is_recording():
            return

        if not self._web_browser or not self._web_browser.is_alive():
            self._handle_browser_died()
            return

        try:
            events = self._web_browser.pop_recorded_events()
        except (InvalidSessionIdException, WebDriverException) as e:
            self._logger.warning("Browser connection lost during recording: %s", e)
            self._handle_browser_died()
            return

        for ev in events:
            # remove it from payload, it's served its purpose after this.
            kind = ev.pop("__kind", None)

            # We are already storing a timestamp
            ev.pop("time", None)

            if kind == "click":
                self._recording_session.append_event(
                    RecordingEventType.DOM_CLICK,
                    payload=ev)

            elif kind == "type":
                self._recording_session.append_event(
                    RecordingEventType.DOM_TYPE,
                    payload=ev)

            elif kind == "check":
                self._recording_session.append_event(
                    RecordingEventType.DOM_CHECK,
                    payload={
                        "xpath": ev["xpath"],
                        "value": ev["value"],
                    })

            elif kind == "select":
                self._recording_session.append_event(
                    RecordingEventType.DOM_SELECT,
                    payload={
                        "xpath": ev["xpath"],
                        "value": ev["value"],
                    })

            self._logger.debug("Recorded event: %s", ev)

    def _on_close_app(self, event):
        # Stop recording cleanly
        if self._recording_session and self._recording_session.is_recording():
            self._recording_session.stop()

        # Close browser if open
        if self._web_browser:
            try:
                self._web_browser.quit()

            except WebDriverException:
                pass
            self._web_browser = None

        event.Skip()  # allow window to close

    def _on_inspector_timer(self, _event):
        if self._state_controller.state != StudioState.INSPECTING:
            return

        if not self._web_browser:
            return

        el = self._web_browser.poll_inspected_element()
        if not el:
            return

        info = self._web_browser.describe_element(el)
        self._inspector_panel.append_element(info)

    def _create_inspector_panel(self):
        self._inspector_panel: InspectorPanel = InspectorPanel(self)

        # Register as a dockable pane on the right
        self._aui_mgr.AddPane(
            self._inspector_panel,
            wx.aui.AuiPaneInfo()
            .Name("InspectorPanel")
            .Caption("WebWeaver Inspector")
            .Right()
            .Row(1)
            .BestSize(350, 600)
            .CloseButton(False)
            .MaximizeButton(True)
            .MinimizeButton(True)
            .Floatable(True)
            .Movable(True)
            .Dockable(True)
            .Hide())

    def _show_inspector_panel(self, show: bool):
        pane = self._aui_mgr.GetPane("InspectorPanel")
        if pane.IsOk():
            pane.Show(show)
            self._aui_mgr.Update()
            PlaybackToolbar.set_all_disabled(self._playback_toolbar)

    def _on_workspace_active_changed(self, _evt):

        pane = self._aui_mgr.GetPane("StepsToolbar")

        if not self._workspace_panel.has_active_recording():
            self._show_playback_toolbar(False)
            self._state_controller.on_solution_loaded()

            if pane.IsOk() and pane.IsShown():
                pane.Hide()
                self._aui_mgr.Update()

        else:
            if pane.IsOk() and not pane.IsShown():
                pane.Show()
                self._aui_mgr.Update()

            self._request_recording_toolbar_update()

        self._update_toolbar_state()
        self._update_playback_toolbar_state()
        self.rebuild_code_generation_menu()

    def _on_start_recording_playback(self, _evt):
        """
        Handle the recording playback 'play' button being pressed.
        """
        ctx = self._workspace_panel.get_active_recording_context()
        if not ctx:
            return

        viewer = self._workspace_panel.get_active_viewer()
        if viewer:
            viewer.timeline_reset_playback_state()

        self._state_controller.on_recording_playback_running()

        recording = load_recording_from_context(ctx)

        self._playback_session = RecordingPlaybackSession(self._web_browser,
                                                          recording,
                                                          self._logger)
        self._playback_session.callback_events.on_step_started = self._on_playback_step_started
        self._playback_session.callback_events.on_step_passed = self._on_playback_step_passed
        self._playback_session.callback_events.on_step_failed = self._on_playback_step_failed
        self._playback_session.callback_events.on_playback_finished = self._on_playback_finished

        self._playback_session.start()
        self._playback_timer.Start(200)

    def _on_pause_recording_playback(self, _evt):
        """
        Handle the recording playback 'pause' button being pressed.
        """
        self._state_controller.on_recording_playback_pause()
        # self._pause_playback(ctx)

    def _on_stop_recording_playback(self, _evt):
        """
        Handle the recording playback 'stop' button being pressed.
        """
        self._state_controller.on_recording_playback_idle()
        # self._stop_playback()

    def _on_playback_timer(self, _evt):
        if not self._playback_session:
            return

        still_running = self._playback_session.step()
        if not still_running:
            self._playback_timer.Stop()
            self._state_controller.on_recording_playback_idle()

    def _on_playback_step_started(self, index: int):
        viewer = self._workspace_panel.get_active_viewer()
        if viewer:
            viewer.timeline_set_current(index)

    def _on_playback_step_passed(self, index: int):
        viewer = self._workspace_panel.get_active_viewer()
        if viewer:
            viewer.timeline_mark_passed(index)

    def _on_playback_step_failed(self, index: int, error: str):
        # Stop playback immediately
        self._playback_timer.Stop()
        self._playback_session = None
        self._state_controller.on_recording_playback_idle()

        viewer = self._workspace_panel.get_active_viewer()
        if viewer:
            viewer.timeline_mark_failed(index)
            wx.MessageBox(error, "Playback Failed", wx.ICON_ERROR)

    def _on_playback_finished(self):
        self._playback_timer.Stop()

    def _request_recording_toolbar_update(self):
        if self._pending_recording_toolbar_update:
            return

        self._pending_recording_toolbar_update = True
        wx.CallLater(16, self._do_recording_toolbar_update)

    def _do_recording_toolbar_update(self):
        self._pending_recording_toolbar_update = False
        self._update_recording_toolbar_state()

    def _on_recording_step_edit(self, _evt):
        page = self._workspace_panel.get_active_viewer()
        if not page:
            return

        index = page.selected_step
        if index is None:
            return

        page.edit_step(index)   # we’ll add this method

    def _on_recording_step_delete(self, _evt):
        page = self._workspace_panel.get_active_viewer()
        if not page:
            return

        index = page.selected_step
        if index is None:
            return

        page.delete_step(index)   # we’ll add this method
