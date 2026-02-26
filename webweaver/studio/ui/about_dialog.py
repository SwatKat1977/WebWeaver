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
import io
import wx
from webweaver.studio.resources.webweaver_main_logo import WEBWEAVER_MAIN_LOGO
from webweaver.studio.version import __version__


class AboutDialog(wx.Dialog):
    """
    Modal "About" dialog for WebWeaver Studio.

    This dialog displays the application logo, name, current version,
    and a short description of the software. The window size is fixed
    (non-resizable) to maintain consistent layout and presentation.

    The logo is loaded from embedded PNG byte data (WEBWEAVER_MAIN_LOGO),
    scaled to 256x256 using high-quality interpolation, and displayed
    above the application title and version information.

    Parameters
    ----------
    parent : wx.Window
        The parent window for this dialog.
    """
    # pylint: disable=too-few-public-methods

    def __init__(self, parent):
        """
        Modal "About" dialog for WebWeaver Studio.

        This dialog displays the application logo, name, current version,
        and a short description of the software. The window size is fixed
        (non-resizable) to maintain consistent layout and presentation.

        The logo is loaded from embedded PNG byte data (WEBWEAVER_MAIN_LOGO),
        scaled to 256x256 using high-quality interpolation, and displayed
        above the application title and version information.

        Parameters
        ----------
        parent : wx.Window
            The parent window for this dialog.
        """
        super().__init__(
            parent,
            title="About WebWeaver Studio",
            style=wx.DEFAULT_DIALOG_STYLE &
                  ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX))

        self.SetMinSize((400, 350))
        self.SetMaxSize((400, 350))

        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        # --- Logo from embedded bytes ---
        stream = io.BytesIO(WEBWEAVER_MAIN_LOGO)
        image = wx.Image(stream, wx.BITMAP_TYPE_PNG)
        image = image.Scale(256, 256, wx.IMAGE_QUALITY_HIGH)
        bitmap = wx.StaticBitmap(panel, bitmap=wx.Bitmap(image))

        # --- Text ---
        title = wx.StaticText(panel, label="WebWeaver Studio")
        font = title.GetFont()
        font = font.Bold()
        font.SetPointSize(font.GetPointSize() + 2)
        title.SetFont(font)

        version = wx.StaticText(panel, label=f"Version {__version__}")
        desc = wx.StaticText(
            panel,
            label="Web interaction recording and playback tool.\n\n"
                  "Milestone release v0.1.0")

        # --- OK button ---
        ok_btn = wx.Button(panel, wx.ID_OK)
        ok_btn.SetDefault()

        # --- Layout ---
        vbox.Add(bitmap, 0, wx.ALL | wx.CENTER, 15)
        vbox.Add(title, 0, wx.ALL | wx.CENTER, 5)
        vbox.Add(version, 0, wx.ALL | wx.CENTER, 5)
        vbox.Add(desc, 0, wx.ALL | wx.CENTER, 10)
        vbox.Add(ok_btn, 0, wx.ALL | wx.CENTER, 15)

        panel.SetSizer(vbox)
        vbox.Fit(self)
        self.Centre()
