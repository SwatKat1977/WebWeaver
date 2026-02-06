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
from io import BytesIO
import wx
# Import generated icon byte data
from ..resources.browser_logos.browser_chromium_logo import BROWSER_CHROMIUM_LOGO
from ..resources.browser_logos.browser_firefox_logo import BROWSER_FIREFOX_LOGO
from ..resources.browser_logos.browser_google_chrome_logo import \
    BROWSER_GOOGLE_CHROME_LOGO
from ..resources.browser_logos.browser_microsoft_edge_logo import \
    BROWSER_MICROSOFT_EDGE_LOGO


def _load_logo(png_bytes: bytes) -> wx.Bitmap:
    """
    Create a suitable  browser logo  from in-memory PNG data.

    The PNG data is loaded into a wx.Image, scaled to 32×32 pixels using
    high-quality interpolation, and then converted to a wx.Bitmap.

    Parameters
    ----------
    png_bytes : bytes
        Raw PNG image data loaded into memory.

    Returns
    -------
    wx.Bitmap
        A bitmap scaled to 32×32 pixels, suitable for use in toolbars.
    """
    stream = BytesIO(png_bytes)
    image = wx.Image(stream)

    # Force 32x32, high quality (matches C++)
    image = image.Scale(32, 32, wx.IMAGE_QUALITY_HIGH)

    return wx.Bitmap(image)


def load_browser_logo_chromium() -> wx.Bitmap:
    """
    Load the icon used for Chromium.

    Returns
    -------
    wx.Bitmap
        Browser icon.
    """
    return _load_logo(BROWSER_CHROMIUM_LOGO)


def load_browser_logo_firefox() -> wx.Bitmap:
    """
    Load the icon used for Firefox.

    Returns
    -------
    wx.Bitmap
        Browser icon.
    """
    return _load_logo(BROWSER_FIREFOX_LOGO)


def load_browser_logo_google_chrome() -> wx.Bitmap:
    """
    Load the icon used for Google Chrome.

    Returns
    -------
    wx.Bitmap
        Browser icon.
    """
    return _load_logo(BROWSER_GOOGLE_CHROME_LOGO)


def load_browser_logo_microsoft_edge() -> wx.Bitmap:
    """
    Load the icon used for Microsoft Edge.

    Returns
    -------
    wx.Bitmap
        Browser icon.
    """
    return _load_logo(BROWSER_MICROSOFT_EDGE_LOGO)
