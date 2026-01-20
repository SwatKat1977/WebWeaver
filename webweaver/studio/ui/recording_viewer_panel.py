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

    def _create_ui(self):
        """
        Build and lay out the user interface controls for the panel.

        Creates the title header and a set of label/value rows
        displaying recording metadata.
        """
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        title = wx.StaticText(
            self,
            wx.ID_ANY,
            self._context.metadata.name
        )

        font = title.GetFont()
        font.MakeBold()
        font.MakeLarger()
        title.SetFont(font)

        main_sizer.Add(title, 0, wx.ALL, 10)

        # Helper for label/value rows
        def add_field(label: str, value: str):
            row = wx.BoxSizer(wx.HORIZONTAL)

            row.Add(
                wx.StaticText(self, wx.ID_ANY, str(label)),
                0,
                wx.RIGHT,
                5
            )

            row.Add(
                wx.StaticText(self, wx.ID_ANY, str(value)),
                1
            )

            main_sizer.Add(
                row,
                0,
                wx.LEFT | wx.RIGHT | wx.BOTTOM,
                10
            )

        # Fields
        recording_file = self._context.recording_file

        add_field("File:", recording_file.name)
        add_field("Path:", recording_file.parent)
        add_field(
            "Recorded:",
            format_time_point(self._context.metadata.created_at)
        )

        self.SetSizerAndFit(main_sizer)
