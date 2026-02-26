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
from .resources.toolbar.toolbar_inspect import INSPECT_ICON
from .resources.toolbar.toolbar_new_project import NEW_PROJECT_ICON
from .resources.toolbar.toolbar_open_project import OPEN_PROJECT_ICON
from .resources.toolbar.toolbar_close_solution import CLOSE_SOLUTION_ICON
from .resources.toolbar.toolbar_pause_record import PAUSE_RECORD_ICON
from .resources.toolbar.toolbar_play_button import PLAY_BUTTON_ICON
from .resources.toolbar.toolbar_save_project import SAVE_PROJECT_ICON
from .resources.toolbar.toolbar_start_record import START_RECORD_ICON
from .resources.toolbar.toolbar_stop_record import STOP_RECORD_ICON
from .resources.toolbar.toolbar_resume_record import RESUME_RECORD_ICON
from .resources.toolbar.toolbar_browser_button import BROWSER_BUTTON_ICON


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


def load_toolbar_inspect_icon() -> wx.Bitmap:
    """
    Load the toolbar icon used for Inspector Mode.

    Returns
    -------
    wx.Bitmap
        The inspector toolbar icon.
    """
    return _load_toolbar_icon(INSPECT_ICON)


def load_toolbar_new_solution_icon() -> wx.Bitmap:
    """
    Load the toolbar icon used for creating a new solution.

    Returns
    -------
    wx.Bitmap
        The 'new solution' toolbar icon.
    """
    return _load_toolbar_icon(NEW_PROJECT_ICON)


def load_toolbar_open_solution_icon() -> wx.Bitmap:
    """
    Load the toolbar icon used for opening an existing solution.

    Returns
    -------
    wx.Bitmap
        The 'open solution' toolbar icon.
    """
    return _load_toolbar_icon(OPEN_PROJECT_ICON)


def load_toolbar_pause_record_icon() -> wx.Bitmap:
    """
    Load the toolbar icon used to pause recording.

    Returns
    -------
    wx.Bitmap
        The 'pause recording' toolbar icon.
    """
    return _load_toolbar_icon(PAUSE_RECORD_ICON)


def load_toolbar_play_icon() -> wx.Bitmap:
    """
    Load the toolbar icon used to play a recording.

    Returns
    -------
    wx.Bitmap
        The 'play recording' toolbar icon.
    """
    return _load_toolbar_icon(PLAY_BUTTON_ICON)


def load_toolbar_save_solution_icon() -> wx.Bitmap:
    """
    Load the toolbar icon used to save the current solution.

    Returns
    -------
    wx.Bitmap
        The 'save solution' toolbar icon.
    """
    return _load_toolbar_icon(SAVE_PROJECT_ICON)


def load_toolbar_start_record_icon() -> wx.Bitmap:
    """
    Load the toolbar icon used to start recording.

    Returns
    -------
    wx.Bitmap
        The 'start recording' toolbar icon.
    """
    return _load_toolbar_icon(START_RECORD_ICON)


def load_toolbar_stop_record_icon() -> wx.Bitmap:
    """
    Load the toolbar icon used to stop recording.

    Returns
    -------
    wx.Bitmap
        The 'stop recording' toolbar icon.
    """
    return _load_toolbar_icon(STOP_RECORD_ICON)


def load_toolbar_resume_record_icon() -> wx.Bitmap:
    """
    Load the toolbar icon used to resume a paused recording.

    Returns
    -------
    wx.Bitmap
        The 'resume recording' toolbar icon.
    """
    return _load_toolbar_icon(RESUME_RECORD_ICON)


def load_toolbar_close_solution_icon() -> wx.Bitmap:
    """
    Load the toolbar icon used to close the current solution.

    Returns
    -------
    wx.Bitmap
        The 'close solution' toolbar icon.
    """
    return _load_toolbar_icon(CLOSE_SOLUTION_ICON)


def load_toolbar_web_browser_icon() -> wx.Bitmap:
    """
    Load the toolbar icon used to open/close the web browser.

    Returns
    -------
    wx.Bitmap
        The 'web browser' toolbar icon.
    """
    return _load_toolbar_icon(BROWSER_BUTTON_ICON)
