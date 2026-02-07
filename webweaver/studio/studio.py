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
from .ui.studio_main_frame import StudioMainFrame
from .ui.studio_splash_screen import StudioSplashScreen
from webweaver.version import __version__ as core_version


class WebWeaverStudioApp(wx.App):
    """
    Application entry point for WebWeaver Automation Studio.

    This class is responsible for initialising the wxPython application,
    creating the main frame, and handling platform-specific startup
    behaviour.
    """
    # pylint: disable=too-few-public-methods

    def OnInit(self) -> bool:
        # pylint: disable=invalid-name
        """
        Initialise the application.

        Creates and displays the main application frame, then schedules
        deferred initialisation of AUI-managed components. Certain UI
        operations are delayed to ensure correct behaviour on macOS.

        Returns
        -------
        bool
            True if initialisation succeeds and the main loop should start.
        """

        splash = StudioSplashScreen(
            # core_version=webweaver_core.__version__,
            core_version=core_version,
            # studio_version=webweaver_studio.__version__
            studio_version="STUDIO VERSION")
        splash.Show()

        frame = StudioMainFrame(parent=None)
        frame.Hide()

        # Tell the splash what to show when it closes
        splash.set_main_frame(frame)

        return True

    def _force_mac_foreground(self, frame):
        """
        Force the application window to the foreground on macOS.

        On macOS, newly launched wxPython applications may not reliably
        become the active application. This helper raises the main window,
        requests focus, and yields to the Cocoa event loop to ensure the
        activation is applied.

        Parameters
        ----------
        frame : wx.Frame
            The main application window to bring to the foreground.
        """
        frame.Raise()
        frame.SetFocus()

        # This is the key: yields to Cocoa so activation sticks
        wx.YieldIfNeeded()


if __name__ == "__main__":
    app = WebWeaverStudioApp(False)
    app.MainLoop()
