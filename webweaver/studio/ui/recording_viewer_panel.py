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

    def _extract_step_fields(self, event: dict):
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

    def _on_step_activated(self, evt):
        index = evt.GetIndex()
        self._edit_step(index)

    def _edit_step(self, index: int):

        try:
            recording = RecordingPersistence.load_from_disk(
                self._context.recording_file)

        except RecordingLoadError as e:
            wx.MessageBox(str(e), "Error", wx.ICON_ERROR)
            return

        step = recording.data["recording"]["events"][index]

        dlg = StepEditDialog(self, step)
        if dlg.ShowModal() == wx.ID_OK and dlg.changed:
            # Step was modified in-place
            RecordingPersistence.save_to_disk(recording)
            self._populate_steps()
