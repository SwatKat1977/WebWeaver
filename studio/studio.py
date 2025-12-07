"""
This source file is part of Web Weaver
For the latest info, see https://github.com/SwatKat1977/WebWeaver

Copyright 2025 SwatKat1977

    This program is free software : you can redistribute it and /or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.If not, see < https://www.gnu.org/licenses/>.
"""
import wx
import wx.lib.newevent
from studio_main_frame import StudioMainFrame

try:
    import AppKit
except ImportError:
    AppKit = None


class WebweaverStudioApp(wx.App):
    def OnInit(self):
        self.frame = StudioMainFrame()
        self.frame.Show()

        if AppKit:
            AppKit.NSApp.activateIgnoringOtherApps_(True)
            self.frame.RequestUserAttention(wx.USER_ATTENTION_INFO)
            wx.CallAfter(self.frame.Raise)

        # Raise AFTER activation
        wx.CallAfter(self.frame.Raise)

        self.SetTopWindow(self.frame)
        return True


if __name__ == "__main__":
    WebweaverStudioApp(False).MainLoop()
