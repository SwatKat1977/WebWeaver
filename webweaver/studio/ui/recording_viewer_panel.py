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
import dataclasses
from datetime import datetime
import secrets
import string
import typing
import wx
from webweaver.studio.recording_view_context import RecordingViewContext
from webweaver.studio.recording.recording_loader import \
    load_recording_from_context
from webweaver.studio.recording.recording_event_type import RecordingEventType
from webweaver.studio.ui.add_step_dialog import (AddStepDialog,
                                                 default_payload_for)
from webweaver.studio.ui.dom_get_step_editor import DomGetStepEditor
from webweaver.studio.ui.events import WORKSPACE_ACTIVE_CHANGED_EVENT_TYPE
from webweaver.studio.ui.check_step_editor import CheckStepEditor
from webweaver.studio.ui.click_step_editor import ClickStepEditor
from webweaver.studio.ui.navgoto_step_editor import NavGotoStepEditor
from webweaver.studio.ui.rest_api_step_editor import RestApiStepEditor
from webweaver.studio.ui.select_step_editor import SelectStepEditor
from webweaver.studio.ui.scroll_step_editor import ScrollStepEditor
from webweaver.studio.ui.type_step_editor import TypeStepEditor
from webweaver.studio.ui.wait_step_editor import WaitStepEditor
from webweaver.studio.persistence.recording_persistence import (
                                                 RecordingPersistence,
                                                 RecordingLoadError)
from webweaver.studio.persistence.recording_document import (RecordingDocument,
                                                             DomGetPayload)


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
    ID_ADD_GETTER_STEP: int = wx.ID_HIGHEST + 5002

    ALLOWED_GETTER_TYPES = {"dom.click",
                            "dom.type",
                            "dom.select",
                            "dom.check"}

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
        """
        Return whether a step is currently selected in the step timeline.

        This is a convenience property that checks whether the underlying
        step list control has at least one selected item.

        :return: True if a step is selected, False otherwise.
        """
        return self._step_list.GetFirstSelected() != -1

    @property
    def selected_step(self) -> int | None:
        """
        Return the index of the currently selected step.

        If no step is selected, this property returns None. If multiple steps
        are selected (which is not normally expected), the index of the first
        selected step is returned.

        The returned index refers to the position in the current step list /
        timeline order.

        :return: The zero-based index of the selected step, or None if no step
                 is selected.
        """
        idx = self._step_list.GetFirstSelected()
        if idx == -1:
            return None
        return idx

    @property
    def step_count(self) -> int:
        """
        Return the total number of steps in the current recording.

        This reflects the number of items currently displayed in the step
        timeline list control.

        :return: The number of steps in the recording timeline.
        """
        return self._step_list.GetItemCount()

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

    def reload_from_disk(self):
        """
        Reload the recording document from disk and refresh the UI.
        """
        self._document = RecordingPersistence.load_from_disk(
            self._document.path
        )

        self.reload_from_document()

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
        event_type = RecordingEventType(event.get("type"))
        action = event_type.name.replace("_", " ").title()
        payload = event.get("payload", {})

        value = ""
        target = ""

        if event_type == RecordingEventType.DOM_CLICK:
            target = payload.get("xpath", "")

        elif event_type == RecordingEventType.DOM_TYPE:
            value = payload.get("value", "")
            target = payload.get("xpath", "")

        elif event_type == RecordingEventType.DOM_SELECT:
            value = payload.get("value") or payload.get("text", "")
            target = payload.get("xpath", "")

        elif event_type == RecordingEventType.DOM_CHECK:
            value = "Checked" if payload.get("value") else "Unchecked"
            target = payload.get("xpath", "")

        elif event_type == RecordingEventType.NAV_GOTO:
            target = payload.get("url", "")

        elif event_type == RecordingEventType.WAIT:
            value = f"{payload.get('duration_ms', 0)} ms"

        return action, value, target

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

        self._step_list.Bind(wx.EVT_LIST_ITEM_SELECTED,
                             self._on_step_selected)
        self._step_list.Bind(wx.EVT_LIST_ITEM_DESELECTED,
                             self._on_step_deselected)

    def _on_step_right_click(self, event: wx.ListEvent):
        index = event.GetIndex()
        if index < 0:
            return

        # Remember which step was right-clicked
        self._context_step_index = index
        step = self._document.get_step(index)

        menu = wx.Menu()

        # Always allow step to be deleted
        menu.Append(self.ID_STEP_DELETE, "Delete Step")
        self.Bind(wx.EVT_MENU, self._on_delete_step, id=self.ID_STEP_DELETE)

        # Only allow getter for certain step types
        if self._can_add_getter(step):
            menu.Append(self.ID_ADD_GETTER_STEP, "Add Getter Below")
            self.Bind(wx.EVT_MENU, self._on_add_getter,
                      id=self.ID_ADD_GETTER_STEP)

        self.PopupMenu(menu)
        menu.Destroy()

    def _on_delete_step(self, _evt):
        index = self._context_step_index
        self._context_step_index = None

        if index is None:
            return

        self.delete_step(index)

    def reload_from_document(self):
        """
        Reload the step timeline UI from the underlying RecordingDocument.

        This method clears the current contents of the step list control and
        repopulates it from the document model. It should be called whenever
        the document's step list is modified externally (e.g. after deleting,
        inserting, or reordering steps) to ensure the UI stays in sync with the
        authoritative document state.
        """
        self._step_list.DeleteAllItems()
        self._populate_steps()

    def _create_step_editor_dialog(
            self,
            event_type: RecordingEventType,
            index: int,
            event: dict) -> typing.Optional[wx.Dialog]:

        step_editor = None

        payload = event.get("payload", {})
        if "control_type" not in payload and \
                event_type not in [RecordingEventType.NAV_GOTO,
                                   RecordingEventType.REST_API,
                                   RecordingEventType.SCROLL,
                                   RecordingEventType.WAIT]:
            payload["control_type"] = "unknown"

        if event_type == RecordingEventType.DOM_CLICK:
            step_editor = ClickStepEditor(self, index, event)

        if event_type == RecordingEventType.DOM_GET:
            step_editor = DomGetStepEditor(self, index, event)

        if event_type == RecordingEventType.DOM_TYPE:
            step_editor = TypeStepEditor(self, index, event)

        if event_type == RecordingEventType.DOM_SELECT:
            step_editor = SelectStepEditor(self, index, event)

        if event_type == RecordingEventType.DOM_CHECK:
            step_editor = CheckStepEditor(self, index, event)

        if event_type == RecordingEventType.NAV_GOTO:
            step_editor = NavGotoStepEditor(self, index, event)

        if event_type == RecordingEventType.REST_API:
            step_editor = RestApiStepEditor(self, index, event)

        if event_type == RecordingEventType.SCROLL:
            step_editor = ScrollStepEditor(self, index, event)

        if event_type == RecordingEventType.WAIT:
            step_editor = WaitStepEditor(self, index, event)

        return step_editor

    def edit_step(self, index: int):
        """
        Open an editor dialog for the specified recording step.

        The method determines the type of the selected event and opens the
        corresponding editor dialog. If the user confirms changes, the
        recording is saved to disk and the UI is refreshed.

        Args:
            index: The index of the step to be edited.

        Returns:
            None. If no editor exists for the step type, a message box is
            displayed and the method returns without making changes.
        """
        event = self._document.get_step(index)
        event_type = RecordingEventType(event["type"])

        dlg = self._create_step_editor_dialog(event_type, index, event)

        if dlg is None:
            wx.MessageBox("No editor for this step type yet")
            return

        if dlg.ShowModal() == wx.ID_OK and dlg.changed:
            RecordingPersistence.save_to_disk(self._document)
            self._populate_steps()

        dlg.Destroy()

    def add_step(self, after_index: typing.Optional[int] = None):
        """
        Add a new step to the current recording document.

        Displays a dialog allowing the user to choose the type of step to
        create, then opens the appropriate step editor to configure its
        payload. If the user cancels at any point, no changes are made.

        The created step is inserted either after the specified index or, if
        `after_index` is None, at the default insertion location as defined by
        the document.

        Args:
            after_index: Optional index after which the new step should be
                         inserted. If None, the step is appended or inserted
                         according to the document's default behavior.

        Side Effects:
            - Opens modal dialogs for step type selection and editing.
            - Modifies the underlying recording document by inserting a new
              step.
            - Saves the updated document to disk.
            - Reloads the UI to reflect the updated document state.
        """
        dlg = AddStepDialog(self)

        if dlg.ShowModal() != wx.ID_OK:
            dlg.Destroy()
            return

        event_type = dlg.get_event_type()
        dlg.Destroy()

        # Create default payload
        payload = default_payload_for(event_type)

        # Create temporary event dict for the editor
        temp_event = {"payload": dataclasses.asdict(payload)}

        editor = self._create_step_editor_dialog(event_type, 0, temp_event)

        if editor is None:
            wx.MessageBox("No editor for this step type yet")
            return

        if editor.ShowModal() != wx.ID_OK:
            editor.Destroy()
            return

        edited_payload_dict = temp_event["payload"]

        # Recreate the correct payload object from the edited data
        payload = default_payload_for(event_type).__class__(**edited_payload_dict)

        # Insert using the edited payload
        self._document.insert_step_after(
            index=after_index,
            event_type=event_type,
            payload=payload)

        RecordingPersistence.save_to_disk(self._document)
        self.reload_from_document()

        editor.Destroy()

    def delete_step(self, index: int):
        """
        Delete a step from the recording at the specified index.

        This method performs the full delete workflow:

            1. Ask the user for confirmation.
            2. Mutate the underlying RecordingDocument.
            3. Persist the updated document to disk.
            4. Refresh the step timeline UI from the document.
            5. Clear any existing selection.
            6. Notify the main frame so dependent UI (e.g. toolbars) can
               recompute their enabled/disabled state.

        If the user cancels the confirmation dialog, no changes are made.

        :param index: Zero-based index of the step to delete.
        """
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

        # 1) Mutate document
        self._document.delete_step(index)

        # 2) Persist
        RecordingPersistence.save_to_disk(self._document)

        # 3) Refresh UI
        self.reload_from_document()

        # 4) Clear selection explicitly
        self._step_list.Select(-1)

        # 5) Notify main frame to recompute toolbar state
        evt = wx.CommandEvent(WORKSPACE_ACTIVE_CHANGED_EVENT_TYPE)
        wx.PostEvent(self.GetTopLevelParent(), evt)

    def move_step(self, from_index: int, to_index: int):
        """
        Move a step within the recording and update the UI.

        Attempts to move a step from one index to another using the
        underlying document model. If the move is successful, the
        recording is saved to disk, the UI is reloaded, and the
        moved step is reselected.

        Args:
            from_index: The current index of the step to move.
            to_index: The target index for the step.

        Returns:
            None. If the move operation is invalid or fails, the
            method returns without making changes.
        """
        if not self._document.move_step(from_index, to_index):
            return

        RecordingPersistence.save_to_disk(self._document)
        self.reload_from_document()

        # Reselect moved step
        self._step_list.Select(to_index)

    def _on_step_activated(self, evt):
        """
        Handle activation (double-click or Enter) of a step in the timeline.

        This opens the step editor dialog for the selected step.
        """
        index = evt.GetIndex()
        self.edit_step(index)

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

    def _on_step_selected(self, _evt):
        evt = wx.CommandEvent(WORKSPACE_ACTIVE_CHANGED_EVENT_TYPE)
        wx.PostEvent(self.GetTopLevelParent(), evt)

    def _on_step_deselected(self, _evt):
        evt = wx.CommandEvent(WORKSPACE_ACTIVE_CHANGED_EVENT_TYPE)
        wx.PostEvent(self.GetTopLevelParent(), evt)

    def _can_add_getter(self, step: dict) -> bool:
        step_type = step.get("type")
        if step_type not in self.ALLOWED_GETTER_TYPES:
            return False

        payload = step.get("payload", {})
        return bool(payload.get("xpath"))

    def _on_add_getter(self, _evt):
        index = self._context_step_index
        self._context_step_index = None

        if index is None:
            return

        # Get the original step
        step = self._document.get_step(index)

        # Defensive check (even though menu was filtered)
        if not self._can_add_getter(step):
            return

        payload = step.get("payload", {})
        xpath = payload.get("xpath")

        if not xpath:
            return

        code: str = ''.join(secrets.choice(string.ascii_letters) \
                            for _ in range(6))
        output_variable: str = f"step_{index}_{code}"

        # Create getter step
        new_step_payload = self._create_getter_step(xpath,
                                                    "text",
                                                    output_variable)

        insert_index = index + 1  # insert below

        # Insert into document
        self._document.insert_step_after(index,
                                         RecordingEventType.DOM_GET,
                                         new_step_payload)

        # Persist
        RecordingPersistence.save_to_disk(self._document)

        # Refresh UI
        self.reload_from_document()

        # Select and scroll to new step
        self._step_list.Select(insert_index)
        self._step_list.EnsureVisible(insert_index)

        # Immediately open editor
        self.edit_step(insert_index)

        # Notify main frame to update toolbars
        evt = wx.CommandEvent(WORKSPACE_ACTIVE_CHANGED_EVENT_TYPE)
        wx.PostEvent(self.GetTopLevelParent(), evt)

    def _create_getter_step(self,
                            xpath: str,
                            property_type: str,
                            output_variable: str) -> DomGetPayload:
        return DomGetPayload(xpath=xpath,
                             property_type=property_type,
                             output_variable=output_variable)
