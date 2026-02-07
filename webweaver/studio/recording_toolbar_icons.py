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
from webweaver.studio.resources.recording_toolbar.add_step import ADD_STEP_ICON
from webweaver.studio.resources.recording_toolbar.delete_step import \
    DELETE_STEP_ICON
from webweaver.studio.resources.recording_toolbar.edit_step import \
    EDIT_STEP_ICON
from webweaver.studio.resources.recording_toolbar.move_step_down import \
    MOVE_STEP_DOWN_ICON
from webweaver.studio.resources.recording_toolbar.move_step_up import \
    MOVE_STEP_UP_ICON


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


def load_toolbar_add_step_icon() -> wx.Bitmap:
    """
    Load the toolbar icon used for adding a step.

    Returns
    -------
    wx.Bitmap
        The toolbar icon.
    """
    return _load_toolbar_icon(ADD_STEP_ICON)


def load_toolbar_delete_step_icon() -> wx.Bitmap:
    """
    Load the toolbar icon used for deleting a step.

    Returns
    -------
    wx.Bitmap
        The toolbar icon.
    """
    return _load_toolbar_icon(DELETE_STEP_ICON)


def load_toolbar_edit_step_icon() -> wx.Bitmap:
    """
    Load the toolbar icon used for editing a step.

    Returns
    -------
    wx.Bitmap
        The toolbar icon.
    """
    return _load_toolbar_icon(EDIT_STEP_ICON)


def load_toolbar_move_step_up_icon() -> wx.Bitmap:
    """
    Load the toolbar icon used for moving step up.

    Returns
    -------
    wx.Bitmap
        The toolbar icon.
    """
    return _load_toolbar_icon(MOVE_STEP_UP_ICON)


def load_toolbar_move_step_down_icon() -> wx.Bitmap:
    """
    Load the toolbar icon used for moving step down.

    Returns
    -------
    wx.Bitmap
        The toolbar icon.
    """
    return _load_toolbar_icon(MOVE_STEP_DOWN_ICON)
