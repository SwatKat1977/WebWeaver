"""
This source file is part of Web Weaver
For the latest info, see https://github.com/SwatKat1977/WebWeaver

Copyright 2025-2026 SwatKat1977

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.
"""
import dataclasses
from datetime import datetime
import secrets
import string
import typing
import wx
from webweaver.studio.recording_step_editor_registry import RecordingStepEditorRegistry
from webweaver.studio.recording_view_context import RecordingViewContext
from webweaver.studio.recording.recording_loader import \
    load_recording_from_context
from webweaver.studio.recording.recording_event_type import RecordingEventType
from webweaver.studio.ui.add_step_dialog import (AddStepDialog,
                                                 default_payload_for)
from webweaver.studio.ui.events import WORKSPACE_ACTIVE_CHANGED_EVENT_TYPE
from webweaver.studio.ui.recording_step_tree import RecordingStepTree, StepStatus
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
        self._steps_tree: typing.Optional[RecordingStepTree] = None

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
    def recording_document(self):
        """
        Get the current recording document.

        Returns:
            RecordingDocument: The active recording document instance.
        """
        return self._document

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
        item = self._steps_tree.GetSelection()
        return item is not None and item.IsOk() and \
            self._steps_tree.GetItemData(item) is not None

    @property
    def selected_step(self) -> int | None:
        """
        Get the index of the currently selected step in the steps tree.

        Returns:
            int | None: The index of the selected step if a valid selection exists;
            otherwise, None.
        """
        item = self._steps_tree.GetSelection()

        if item is None or not item.IsOk():
            return None

        step = self._steps_tree.GetItemData(item)

        if not step:
            return None

        return step["index"]

    @property
    def step_count(self) -> int:
        """
        Return the total number of steps in the current recording.

        This reflects the number of items currently displayed in the step
        timeline list control.

        :return: The number of steps in the recording timeline.
        """
        return len(self._document.data["recording"]["events"])

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
        self._steps_tree.set_step_status(index, StepStatus.RUNNING)

    def timeline_mark_passed(self, index: int):
        """
        Mark the given step index as successfully executed.

        Passed steps are tracked so they can be rendered in a "completed" style
        in the timeline (e.g. green highlight).

        Args:
            index (int): Index of the step that completed successfully.
        """
        self._passed_indices.add(index)
        self._steps_tree.set_step_status(index, StepStatus.PASSED)

    def timeline_mark_failed(self, index: int):
        """
        Mark the given step index as failed.

        Only a single failed step is tracked at a time. This is used to render
        the step in an error style and to indicate where playback stopped.

        Args:
            index (int): Index of the step that failed.
        """
        self._failed_index = index
        self._steps_tree.set_step_status(index, StepStatus.FAILED)

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
        self._steps_tree.reset_statuses()

    def delete_step(self, index: int):
        """Delete a step from the recording.

        Prompts the user for confirmation before deleting the specified step.
        If confirmed, the step is removed from the underlying document, the
        updated document is persisted to disk, and the UI is refreshed to
        reflect the change. Any current selection in the steps tree is cleared.

        Args:
            index (int): The index of the step to delete.

        Returns:
            None
        """
        step = self._document.get_step(index)

        msg = (
            f"Delete step?\n\n"
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

        # 4 Clear selection explicitly
        self._steps_tree.UnselectAll()

    def reload_from_disk(self):
        """
        Reload the recording document from disk and refresh the UI.
        """
        self._document = RecordingPersistence.load_from_disk(
            self._document.path
        )

        self.reload_from_document()

    def _populate_steps(self):
        """
        Populate the timeline list control from the loaded recording.

        This clears any existing rows and rebuilds the list from the events
        stored in the recording associated with this panel's context.
        """
        self._steps_tree.clear()

        recording = load_recording_from_context(self.context)

        for event in recording.events:
            payload = event.get("payload", {})
            payload_label = payload.get("label", "")
            step_type = event.get("type", "")

            label = payload_label if payload_label else step_type
            self._steps_tree.add_step(label, event)

    def _create_ui(self):
        """
        Build and lay out the user interface for the recording editor.

        This initial implementation displays a simple, read-only timeline view
        of the recording steps.
        """
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        self._steps_tree = RecordingStepTree(self)

        main_sizer.Add(self._steps_tree, 1, wx.EXPAND)

        self.SetSizer(main_sizer)

        self._populate_steps()

        self._steps_tree.Bind(wx.EVT_TREE_ITEM_ACTIVATED,
                              self._on_step_activated)

        self._steps_tree.Bind(wx.EVT_TREE_ITEM_RIGHT_CLICK,
                              self._on_step_right_click)

        self._steps_tree.Bind(wx.EVT_TREE_SEL_CHANGED,
                              self._on_tree_selection_changed)


    def _on_step_right_click(self, event: wx.TreeEvent):
        item = event.GetItem()

        if not item.IsOk():
            return

        self._steps_tree.SelectItem(item)

        step = self._steps_tree.GetItemData(item)

        if not step:
            return

        self._context_step_index = step["index"]

        menu = wx.Menu()

        menu.Append(self.ID_STEP_DELETE, "Delete Step")
        self.Bind(wx.EVT_MENU, self._on_delete_step, id=self.ID_STEP_DELETE)

        if self._can_add_getter(step):
            menu.Append(self.ID_ADD_GETTER_STEP, "Add Getter Below")
            self.Bind(wx.EVT_MENU, self._on_add_getter,
                      id=self.ID_ADD_GETTER_STEP)

        self.PopupMenu(menu)
        menu.Destroy()

    def _on_delete_step(self, _event):
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
        self._populate_steps()

    def _create_step_editor_dialog(
            self,
            event_type: RecordingEventType,
            event: dict) -> typing.Optional[wx.Dialog]:

        payload = event.get("payload", {})
        if "control_type" not in payload and \
                event_type not in [RecordingEventType.ASSERT,
                                   RecordingEventType.DOM_GET,
                                   RecordingEventType.NAV_GOTO,
                                   RecordingEventType.REST_API,
                                   RecordingEventType.SENDKEYS,
                                   RecordingEventType.SCROLL,
                                   RecordingEventType.USER_VARIABLE,
                                   RecordingEventType.WAIT]:
            payload["control_type"] = "unknown"

        # Ensure that a default label is always present.
        if "label" not in payload:
            payload["label"] = ""

        # Version 0.1.0 recordings support - To be removed soon
        payload.pop("__kind", None)

        editor_class = RecordingStepEditorRegistry.create_editor(event_type)

        return editor_class(self, event)

    def edit_step(self, index: int):
        """
        Open an editor dialog for the selected step and persist any changes.

        The method resolves the step associated with the given tree item,
        determines its event type, and launches the appropriate editor dialog.
        If the user confirms changes, the updated document is saved and the
        steps view is refreshed.

        Args:
            index (int): The index of the step tree item to edit.

        Returns:
            None
        """
        item = self._steps_tree.find_item_by_index(index)
        self._perform_edit_step(item)

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

        editor = self._create_step_editor_dialog(event_type, temp_event)

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

    def _on_step_activated(self, evt):
        """
        Handle activation (double-click or Enter) of a step in the timeline.

        This opens the step editor dialog for the selected step.
        """
        item = evt.GetItem()

        if not item.IsOk():
            return

        self._perform_edit_step(item)

    def _perform_edit_step(self, item):
        tree_event = self._steps_tree.GetItemData(item)

        if not tree_event:
            return

        # Re-resolve from document
        index = tree_event["index"]
        event = self._document.get_step(index)

        event_type = RecordingEventType(event.get("type"))

        dlg = self._create_step_editor_dialog(event_type, event)

        if dlg is None:
            wx.MessageBox("No editor for this step type yet")
            return

        if dlg.ShowModal() == wx.ID_OK and dlg.changed:
            RecordingPersistence.save_to_disk(self._document)
            self._populate_steps()

        dlg.Destroy()

    def _on_tree_selection_changed(self, _evt):
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

        # Find the newly inserted step in the tree
        target_item = None

        def find_item(parent):
            nonlocal target_item

            child, cookie = self._steps_tree.GetFirstChild(parent)

            while child.IsOk():
                data = self._steps_tree.GetItemData(child)

                if data and data["index"] == insert_index:
                    target_item = child
                    return

                find_item(child)

                if target_item:
                    return

                child, cookie = self._steps_tree.GetNextChild(parent, cookie)

        find_item(self._steps_tree.tree_root)

        # Select + open editor
        if target_item and target_item.IsOk():
            self._steps_tree.SelectItem(target_item)
            self.edit_step(target_item)

    def _create_getter_step(self,
                            xpath: str,
                            property_type: str,
                            output_variable: str) -> DomGetPayload:
        return DomGetPayload(label="",
                             xpath=xpath,
                             property_type=property_type,
                             output_variable=output_variable)
