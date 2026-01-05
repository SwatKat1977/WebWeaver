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
import wx
import wx.aui
from recording_view_context import RecordingViewContext
from recording_viewer_panel import RecordingViewerPanel


class WorkspacePanel(wx.Panel):

    def __init__(self, parent: wx.Window):
        super().__init__(parent)

        self._notebook: wx.aui.AuiNotebook = None

        self._create_ui()

    def open_recording(self, ctx: RecordingViewContext):
        if self.is_recording_open(ctx.recording_file):
            # focus existing tab
            return

        viewer = RecordingViewerPanel(self._notebook, ctx)
        self._notebook.AddPage(viewer, ctx.metadata.name, select=True)

    def is_recording_open(self, file) -> bool:
        if not self._notebook:
            return False

        target = wx.FileName(file)
        target.Normalize(wx.PATH_NORM_ABSOLUTE |
                         wx.PATH_NORM_DOTS |
                         wx.PATH_NORM_TILDE)

        for i in range(self._notebook.GetPageCount()):
            page = self._notebook.GetPage(i)

            if not isinstance(page, RecordingViewerPanel):
                continue

            open_file: wx.FileName = page.get_recording_file()
            open_file.Normalize(wx.PATH_NORM_ABSOLUTE |
                                wx.PATH_NORM_DOTS |
                                wx.PATH_NORM_TILDE)

            if open_file == target:
                return True

        return False

    def on_recording_renamed_by_id(self,
                                   recording_id: str,
                                   new_name: str) -> None:
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
