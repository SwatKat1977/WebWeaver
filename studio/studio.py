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

from studio_main_frame import StudioMainFrame


class WebWeaverStudioApp(wx.App):
    def OnInit(self) -> bool:
        frame = StudioMainFrame(parent=None)
        frame.Show(True)

        # IMPORTANT: delay AUI initialisation until AFTER the window is shown
        wx.CallAfter(frame.init_aui)

        wx.CallAfter(self._force_mac_foreground, frame)

        return True

    def _force_mac_foreground(self, frame):
        """
        Forces macOS to treat this process as the active GUI app.
        """
        frame.Raise()
        frame.SetFocus()

        # This is the key: yields to Cocoa so activation sticks
        wx.YieldIfNeeded()


if __name__ == "__main__":
    app = WebWeaverStudioApp(False)
    app.MainLoop()
