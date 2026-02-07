"""
This source file is part of Web Weaver
For the latest info, see https://github.com/SwatKat1977/WebWeaver

Copyright 2025-2026 Webweaver Development Team

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
from webweaver.studio.image_helpers import ImageHelpers
from webweaver.studio.resources.webweaver_main_logo import WEBWEAVER_MAIN_LOGO


class StudioSplashScreen(wx.Frame):
    """
    Simple splash screen window displayed during application startup.

    This frame presents the main WebWeaver Studio logo along with version
    information for both the core engine and the Studio application.
    After a short delay, the splash screen automatically closes and
    transfers control to the main application window.
    """
    # pylint: disable=too-few-public-methods

    def __init__(self, core_version: str, studio_version: str):
        """
        Initialize the splash screen window.

        The splash screen is displayed without a taskbar entry or window
        border and remains on top of other windows. It shows the main
        application logo and version details, and automatically closes
        after a fixed timeout.

        Parameters
        ----------
        core_version : str
            Version string for the core WebWeaver engine.

        studio_version : str
            Version string for the WebWeaver Studio application.
        """
        super().__init__(
            parent=None,
            title="",
            style=wx.FRAME_NO_TASKBAR | wx.BORDER_NONE | wx.STAY_ON_TOP
        )

        self.main_frame = None

        outer = wx.Panel(self)
        # Subtle gray border
        outer.SetBackgroundColour("#AAAAAA")

        frame_sizer = wx.BoxSizer(wx.VERTICAL)
        frame_sizer.Add(outer, 1, wx.EXPAND)
        self.SetSizer(frame_sizer)

        panel = wx.Panel(outer)
        panel.SetBackgroundColour("#E8E8E8")
        outer_sizer = wx.BoxSizer(wx.VERTICAL)
        outer_sizer.Add(panel, 1, wx.ALL | wx.EXPAND, 2) # 2px border
        outer.SetSizer(outer_sizer)

        logo_bitmap = ImageHelpers.image_to_wxbitmap(WEBWEAVER_MAIN_LOGO,
                                                     width=500,
                                                     height=500)

        logo = wx.StaticBitmap(panel, bitmap=logo_bitmap)

        core = wx.StaticText(panel, label=f"Core: {core_version}")
        studio = wx.StaticText(panel, label=f"Studio: {studio_version}")

        core.SetForegroundColour("#000000")
        studio.SetForegroundColour("#000000")

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(logo, 0, wx.ALIGN_CENTER | wx.ALL, 10)
        sizer.AddStretchSpacer()

        bottom_sizer = wx.BoxSizer(wx.HORIZONTAL)
        bottom_sizer.AddStretchSpacer()
        bottom_sizer.Add(core, 0, wx.RIGHT, 10)
        bottom_sizer.Add(studio, 0, wx.RIGHT, 10)

        sizer.Add(bottom_sizer, 0, wx.EXPAND | wx.BOTTOM, 8)

        panel.SetSizer(sizer)

        panel.Layout()
        outer.Layout()
        self.Layout()

        self.SetSize((700, 550))
        self.Centre()

        # Start a simple one-shot timer
        self._timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self._on_timer, self._timer)
        self._timer.StartOnce(9000)

    def set_main_frame(self, frame):
        """
        Specify the main application frame to be shown after the splash screen.

        This method should be called after the main application window has
        been created so that it can be displayed once the splash screen
        timeout expires.

        Parameters
        ----------
        frame : wx.Frame
            The main application frame instance to show when the splash
            screen closes.
        """
        self.main_frame = frame

    def _on_timer(self, _event):
        """
        Handle the splash screen timeout event.

        When the timer fires, the main application frame (if assigned)
        is displayed and initialized, and the splash screen destroys
        itself.
        """
        if self.main_frame:
            self.main_frame.Show()
            wx.CallAfter(self.main_frame.init_aui)

        self.Destroy()
