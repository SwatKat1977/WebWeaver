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
from io import BytesIO
import wx
from .resources.explorer_tree_icons.pages_icon import PAGES_ICON
from .resources.explorer_tree_icons.recordings_icon import RECORDINGS_ICON
from .resources.explorer_tree_icons.root_icon import ROOT_ICON
from .resources.explorer_tree_icons.scripts_icon import SCRIPTS_ICON


def _load_icon(png_bytes: bytes) -> wx.Bitmap:
    """
    Create a wx.Bitmap suitable for use as an icon from in-memory PNG data.

    The PNG data is loaded into a wx.Image, scaled to 16×16 pixels using
    high-quality interpolation, and then converted to a wx.Bitmap.

    Parameters
    ----------
    png_bytes : bytes
        Raw PNG image data loaded into memory.

    Returns
    -------
    wx.Bitmap
        A bitmap scaled to 16×16 pixels, suitable for use in toolbars.
    """
    stream = BytesIO(png_bytes)
    image = wx.Image(stream)

    # Force 32x32, high quality (matches C++)
    image = image.Scale(16, 16, wx.IMAGE_QUALITY_HIGH)

    return wx.Bitmap(image)


def load_root_icon() -> wx.Bitmap:
    """
    Load the root solution icon

    Returns
    -------
    wx.Bitmap
        The solution explorer icon.
    """
    return _load_icon(ROOT_ICON)


def load_recording_icon() -> wx.Bitmap:
    """
    Load the recording solution icon

    Returns
    -------
    wx.Bitmap
        The solution explorer icon.
    """
    return _load_icon(RECORDINGS_ICON)


def load_recordings_filter_icon() -> wx.Bitmap:
    """
    Load the recordings filter solution icon

    Returns
    -------
    wx.Bitmap
        The solution explorer icon.
    """
    return _load_icon(RECORDINGS_ICON)


def load_pages_filter_icon() -> wx.Bitmap:
    """
    Load the page filter solution icon

    Returns
    -------
    wx.Bitmap
        The solution explorer icon.
    """
    return _load_icon(PAGES_ICON)


def load_scripts_filter_icon() -> wx.Bitmap:
    """
    Load the scripts filter solution icon

    Returns
    -------
    wx.Bitmap
        The solution explorer icon.
    """
    return _load_icon(SCRIPTS_ICON)
