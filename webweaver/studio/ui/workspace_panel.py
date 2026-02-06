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
from pathlib import Path
from typing import Optional
import wx
import wx.aui
from ..recording_view_context import RecordingViewContext
from .recording_viewer_panel import RecordingViewerPanel
from .events import WORKSPACE_ACTIVE_CHANGED_EVENT_TYPE


class WorkspacePanel(wx.Panel):
    """
    Main workspace panel that hosts open recording viewers in a tabbed interface.

    This panel manages an AuiNotebook containing one tab per open recording.
    It is responsible for opening recordings, preventing duplicates, and
    reacting to recording lifecycle events such as rename and deletion.
    """

    def __init__(self, parent: wx.Window):
        """
        Create the workspace panel.

        :param parent: Parent wx window.
        """
        super().__init__(parent)

        self._notebook: Optional[wx.aui.AuiNotebook] = None

        self._create_ui()

        self._notebook.Bind(wx.aui.EVT_AUINOTEBOOK_PAGE_CHANGED,
                            self._on_page_changed)
        self._notebook.Bind(wx.aui.EVT_AUINOTEBOOK_PAGE_CLOSED,
                            self._on_page_changed)

    def open_recording(self, ctx: RecordingViewContext):
        """
        Open a recording in the workspace.

        If the recording is already open, this method does nothing (the
        existing tab is left as-is). Otherwise, a new RecordingViewerPanel
        is created and added as a notebook tab.

        :param ctx: Recording view context containing metadata and file path.
        """
        if self.is_recording_open(ctx.recording_file):
            # focus existing tab
            return

        viewer = RecordingViewerPanel(self._notebook, ctx)
        self._notebook.AddPage(viewer, ctx.metadata.name, select=True)

    def is_recording_open(self, file) -> bool:
        """
        Check whether a recording file is already open in the workspace.

        File paths are normalized before comparison to ensure consistent
        matching regardless of relative paths or symbolic components.

        :param file: Path to the recording file.
        :return: True if the recording is already open, otherwise False.
        """
        if not self._notebook:
            return False

        target = Path(file).expanduser().resolve()

        for i in range(self._notebook.GetPageCount()):
            page = self._notebook.GetPage(i)

            if not isinstance(page, RecordingViewerPanel):
                continue

            open_file = Path(page.get_recording_file()).expanduser().resolve()
            if open_file == target:
                return True

        return False

    def on_recording_renamed_by_id(self,
                                   recording_id: str,
                                   new_name: str) -> None:
        """
        Update the tab title for an open recording that has been renamed.

        If the recording is not currently open, this method does nothing.

        :param recording_id: Unique ID of the recording.
        :param new_name: New display name for the recording.
        """
        if not self._notebook:
            return

        for i in range(self._notebook.GetPageCount()):
            page = self._notebook.GetPage(i)

            if not isinstance(page, RecordingViewerPanel):
                continue

            if page.get_recording_id() == recording_id:
                self._notebook.SetPageText(i, new_name)
                return

    def on_recording_deleted_by_id(self, recording_id: str) -> None:
        """
        Close the tab for a recording that has been deleted.

        If the recording is not currently open, this method does nothing.

        :param recording_id: Unique ID of the deleted recording.
        """
        if not self._notebook:
            return

        for i in range(self._notebook.GetPageCount()):
            page = self._notebook.GetPage(i)

            if not isinstance(page, RecordingViewerPanel):
                continue

            if page.get_recording_id() == recording_id:
                self._notebook.DeletePage(i)
                return

    def _create_ui(self):
        """
        Construct and lay out the workspace UI components.

        This includes the workspace title and the tabbed notebook used
        to host recording viewer panels.
        """
        sizer = wx.BoxSizer(wx.VERTICAL)

        title = wx.StaticText(self, wx.ID_ANY, "Workspace")
        font = title.GetFont()
        font.MakeBold()
        title.SetFont(font)

        sizer.Add(title, 0, wx.ALL, 6)

        self._notebook = wx.aui.AuiNotebook(
            self,
            wx.ID_ANY,
            wx.DefaultPosition,
            wx.DefaultSize,
            wx.aui.AUI_NB_TOP | wx.aui.AUI_NB_TAB_MOVE |
            wx.aui.AUI_NB_CLOSE_ON_ALL_TABS)

        sizer.Add(self._notebook, 1, wx.EXPAND)
        self.SetSizer(sizer)

    def clear(self):
        """"
        Clear any notebook pages, if a notebook exists.
        """
        if not self._notebook:
            return

        self._notebook.DeleteAllPages()

    def get_active_recording_context(self) -> Optional[RecordingViewContext]:
        """
        Return the RecordingViewContext for the currently active tab,
        or None if the active tab is not a recording.
        """
        if not self._notebook:
            return None

        page = self._notebook.GetCurrentPage()
        if isinstance(page, RecordingViewerPanel):
            return page.context

        return None

    def get_active_viewer(self):
        """
        Return the active RecordingViewerPanel, or None if the active tab
        is not a recording viewer.
        """
        if not self._notebook:
            return None

        page = self._notebook.GetCurrentPage()
        if isinstance(page, RecordingViewerPanel):
            return page

        return None

    def has_active_recording(self) -> bool:
        """
        Return whether there is currently an active recording open in the workspace.

        This is a convenience helper that checks whether an active
        RecordingViewContext exists.
        """
        return self.get_active_recording_context() is not None

    def _on_page_changed(self, _evt):
        """
        Handle notebook page change events and notify the parent window.

        This method is called when the active tab in the workspace notebook
        changes. It emits a WORKSPACE_ACTIVE_CHANGED event to the parent so
        that other parts of the UI can update their state accordingly
        (e.g. toolbars, menus, inspectors).
        """
        evt = wx.CommandEvent(WORKSPACE_ACTIVE_CHANGED_EVENT_TYPE)
        wx.PostEvent(self.GetParent(), evt)
