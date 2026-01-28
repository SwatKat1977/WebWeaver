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
from datetime import datetime
import wx
from recording_view_context import RecordingViewContext
from recording.recording_loader import load_recording_from_context
from ui.step_edit_dialog import StepEditDialog
from persistence.recording_persistence import (RecordingPersistence,
                                               RecordingLoadError)
from persistence.recording_document import RecordingDocument


def format_time_point(dt: datetime) -> str:
    """
    Format a datetime value into a human-readable timestamp string.

    This is the Python equivalent of formatting a
    std::chrono::system_clock::time_point in C++.

    Args:
        dt (datetime): The datetime instance to format.

    Returns:
        str: A formatted timestamp in the form
             'YYYY-MM-DD HH:MM:SS'.
    """
    return dt.strftime("%Y-%m-%d %H:%M:%S")


class RecordingViewerPanel(wx.Panel):
    """
    Panel responsible for displaying metadata and file information
    for a single recording.

    This panel presents a read-only view of the recording's name,
    file location, and creation time.
    """

    ID_STEP_DELETE: int = wx.ID_HIGHEST + 5001

    def __init__(self, parent, ctx: RecordingViewContext):
        """
        Construct the RecordingViewerPanel.

        Args:
            parent (wx.Window): Parent window that owns this panel.
            ctx (RecordingViewContext): Context object containing
                recording metadata and file information.
        """
        super().__init__(parent)
        self._context: RecordingViewContext = ctx
        self._step_list: wx.ListCtrl = None

        self._current_index: int | None = None
        self._failed_index: int | None = None
        self._passed_indices: set[int] = set()

        self._context_step_index = None

        try:
            self._document: RecordingDocument = \
                RecordingPersistence.load_from_disk(
                    self._context.recording_file)

        except RecordingLoadError as e:
            wx.MessageBox(str(e), "Error", wx.ICON_ERROR)
            return

        self._create_ui()

    @property
    def context(self) -> RecordingViewContext:
        """
        Return the view context associated with this recording viewer.

        The RecordingViewContext provides access to the recording's metadata,
        file path, and other information required by the viewer to display and
        interact with the recording.
        """
        return self._context

    @property
    def step_is_selected(self) -> bool:
        return self._context_step_index is not None

    def get_recording_id(self) -> str:
        """
        Retrieve the unique identifier of the recording.

        Returns:
            str: Recording ID.
        """
        return self._context.metadata.id

    def get_recording_file(self):
        """
        Retrieve the file associated with the recording.

        Returns:
            wx.FileName: The recording file.
        """
        return self._context.recording_file

    def timeline_set_current(self, index: int):
        """
        Mark the given step index as the currently executing step.

        This is used during playback to visually highlight the step that is
        currently being executed.

        Args:
            index (int): Index of the step that is currently active.
        """
        self._current_index = index
        self._refresh_timeline_styles()

    def timeline_mark_passed(self, index: int):
        """
        Mark the given step index as successfully executed.

        Passed steps are tracked so they can be rendered in a "completed" style
        in the timeline (e.g. green highlight).

        Args:
            index (int): Index of the step that completed successfully.
        """
        self._passed_indices.add(index)
        self._refresh_timeline_styles()

    def timeline_mark_failed(self, index: int):
        """
        Mark the given step index as failed.

        Only a single failed step is tracked at a time. This is used to render
        the step in an error style and to indicate where playback stopped.

        Args:
            index (int): Index of the step that failed.
        """
        self._failed_index = index
        self._refresh_timeline_styles()

    def timeline_reset_playback_state(self):
        """
        Clear all playback-related visual state from the timeline.

        This removes:
        - The current step marker
        - Any failed step marker
        - All passed step markers

        After this call, the timeline returns to its neutral, unplayed state.
        """
        self._current_index = None
        self._failed_index = None
        self._passed_indices.clear()
        self._refresh_timeline_styles()

    def _extract_step_fields(self, event: dict):
        """
        Extract displayable fields from a raw recording event.

        Converts the low-level event dictionary into human-readable values
        suitable for display in the timeline list control.

        Args:
            event (dict): Raw event dictionary from the recording file.

        Returns:
            tuple[str, str, str]: A tuple of (action, value, target).
        """
        t = event.get("type")
        p = event.get("payload", {})

        if t == "dom.click":
            return "Click", "", p.get("xpath")

        if t == "dom.type":
            return "Type", p.get("value"), p.get("xpath")

        if t == "dom.select":
            value = p.get("value") or p.get("text")
            return "Select", value, p.get("xpath")

        if t == "dom.check":
            return "Check", str(p.get("value")), p.get("xpath")

        if t == "nav.goto":
            return "Navigate", event.get("url"), ""

        return t, str(p), ""

    def _populate_steps(self):
        """
        Populate the timeline list control from the loaded recording.

        This clears any existing rows and rebuilds the list from the events
        stored in the recording associated with this panel's context.
        """
        self._step_list.DeleteAllItems()

        recording = load_recording_from_context(self.context)

        for i, event in enumerate(recording.events):
            idx = self._step_list.InsertItem(i, str(i))

            action, value, target = self._extract_step_fields(event)

            self._step_list.SetItem(idx, 1, action)
            self._step_list.SetItem(idx, 2, value or "")
            self._step_list.SetItem(idx, 3, target or "")

    def _create_ui(self):
        """
        Build and lay out the user interface for the recording editor.

        This initial implementation displays a simple, read-only timeline view
        of the recording steps.
        """
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        self._step_list = wx.ListCtrl(
            self,
            style=wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.BORDER_THEME
        )

        self._step_list.InsertColumn(0, "#", width=50)
        self._step_list.InsertColumn(1, "Action", width=120)
        self._step_list.InsertColumn(2, "Value", width=200)
        self._step_list.InsertColumn(3, "Target", width=600)

        main_sizer.Add(self._step_list, 1, wx.EXPAND | wx.ALL, 5)

        self.SetSizer(main_sizer)

        self._populate_steps()

        self._step_list.Bind(wx.EVT_LIST_ITEM_ACTIVATED,
                             self._on_step_activated)

        self._step_list.Bind(wx.EVT_LIST_ITEM_RIGHT_CLICK,
                             self._on_step_right_click)

    def _on_step_right_click(self, event: wx.ListEvent):
        index = event.GetIndex()
        if index < 0:
            return

        # Remember which step was right-clicked
        self._context_step_index = index

        menu = wx.Menu()
        menu.Append(self.ID_STEP_DELETE, "Delete Step")

        self.Bind(wx.EVT_MENU, self._on_delete_step, id=self.ID_STEP_DELETE)

        self.PopupMenu(menu)
        menu.Destroy()

    def _on_delete_step(self, _evt):
        index = self._context_step_index
        self._context_step_index = None

        if index is None:
            return

        step = self._document.get_step(index)

        msg = (
            f"Delete step {index + 1}?\n\n"
            f"Type: {step.get('type')}"
        )

        dlg = wx.MessageDialog(
            self,
            msg,
            "Delete Step",
            wx.YES_NO | wx.NO_DEFAULT | wx.ICON_WARNING
        )

        if dlg.ShowModal() != wx.ID_YES:
            dlg.Destroy()
            return

        dlg.Destroy()

        # 1) Mutate document (in memory)
        self._document.delete_step(index)

        # 2) Persist to disk
        RecordingPersistence.save_to_disk(self._document)

        # 3) Refresh UI
        self.reload_from_document()

    def reload_from_document(self):
        self._step_list.DeleteAllItems()
        self._populate_steps()

    def _on_step_activated(self, evt):
        """
        Handle activation (double-click or Enter) of a step in the timeline.

        This opens the step editor dialog for the selected step.
        """
        index = evt.GetIndex()
        self._edit_step(index)

    def _edit_step(self, index: int):
        """
        Open the step editor dialog for the given step index.

        This method:
        - Loads the recording from disk
        - Opens the StepEditDialog for the selected step
        - Saves the recording back to disk if the step was modified
        - Refreshes the timeline view

        Args:
            index (int): Index of the step to edit.
        """
        step = self._document.data["recording"]["events"][index]

        dlg = StepEditDialog(self, step)
        if dlg.ShowModal() == wx.ID_OK and dlg.changed:
            # Step was modified in-place
            RecordingPersistence.save_to_disk(self._document)
            self._populate_steps()

    def _refresh_timeline_styles(self):
        """
        Refresh the visual styling of timeline items based on playback state.

        This method updates row styles to reflect:
        - Current step
        - Passed steps
        - Failed step

        It is called whenever playback state changes.
        """
        count = self._step_list.GetItemCount()

        for i in range(count):
            if self._failed_index is not None and i == self._failed_index:
                # Failed step -> red
                self._step_list.SetItemBackgroundColour(i, wx.Colour(255, 200, 200))

            elif self._current_index is not None and i == self._current_index:
                # Currently executing -> blue
                self._step_list.SetItemBackgroundColour(i, wx.Colour(200, 220, 255))

            elif i in self._passed_indices:
                # Already passed -> green
                self._step_list.SetItemBackgroundColour(i, wx.Colour(200, 255, 200))

            else:
                # Not touched yet
                self._step_list.SetItemBackgroundColour(i, wx.NullColour)

        # Auto-scroll to current step
        if self._current_index is not None:
            self._step_list.EnsureVisible(self._current_index)
