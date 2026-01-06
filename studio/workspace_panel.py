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
import wx
import wx.aui
from recording_view_context import RecordingViewContext
from recording_viewer_panel import RecordingViewerPanel


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

        self._notebook: wx.aui.AuiNotebook = None

        self._create_ui()

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
            wx.aui.AUI_NB_TOP | wx.aui.AUI_NB_TAB_MOVE)

        sizer.Add(self._notebook, 1, wx.EXPAND)
        self.SetSizer(sizer)
