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
# Import generated icon byte data
from resources.playback_toolbar.toolbar_pause import PAUSE_ICON
from resources.playback_toolbar.toolbar_play import PLAY_ICON
from resources.playback_toolbar.toolbar_step import STEP_ICON
from resources.playback_toolbar.toolbar_stop import STOP_ICON


def _load_toolbar_icon(png_bytes: bytes) -> wx.Bitmap:
    """
    Create a wx.Bitmap suitable for use in a toolbar from in-memory PNG data.

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


def load_playback_toolbar_pause_icon() -> wx.Bitmap:
    """
    Load the toolbar icon used for pause playback.

    Returns
    -------
    wx.Bitmap
        The toolbar icon.
    """
    return _load_toolbar_icon(PAUSE_ICON)


def load_playback_toolbar_play_icon() -> wx.Bitmap:
    """
    Load the toolbar icon used for play playback.

    Returns
    -------
    wx.Bitmap
        The toolbar icon.
    """
    return _load_toolbar_icon(PLAY_ICON)


def load_playback_toolbar_step_icon() -> wx.Bitmap:
    """
    Load the toolbar icon used for step playback.

    Returns
    -------
    wx.Bitmap
        The toolbar icon.
    """
    return _load_toolbar_icon(STEP_ICON)


def load_playback_toolbar_stop_icon() -> wx.Bitmap:
    """
    Load the toolbar icon used for stop playback.

    Returns
    -------
    wx.Bitmap
        The toolbar icon.
    """
    return _load_toolbar_icon(STOP_ICON)
