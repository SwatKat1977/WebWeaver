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
import typing
import wx


class ImageHelpers:
    """
    Utility helper functions for working with images in a wxPython context.

    This class provides static convenience methods for converting and
    manipulating image data so that it can be easily used within wxPython
    user interface components such as toolbars, menus, and dialogs.
    """
    # pylint: disable=too-few-public-methods

    @staticmethod
    def image_to_wxbitmap(image_bytes: bytes,
                          width: typing.Optional[int] = None,
                          height: typing.Optional[int] = None) -> wx.Bitmap:
        """
        Create a wx.Bitmap suitable for use as an icon from in-memory image
        data.

        The PNG data is loaded into a wx.Image, scaled to 16×16 pixels using
        high-quality interpolation, and then converted to a wx.Bitmap.

        Parameters
        ----------
        image_bytes : bytes
            Raw PNG image data loaded into memory.

        width: typing.Optional[int]
            Force width to scale to (width) pixels, default in None

        height: typing.Optional[int]
            Force height to scale to (height) pixels, default in None

        Returns
        -------
        wx.Bitmap
            A wx bitmap, suitable for use in toolbars etc.
        """
        stream = BytesIO(image_bytes)
        image = wx.Image(stream)

        # Force WxH, high quality
        if width and height:
            image = image.Scale(width, height, wx.IMAGE_QUALITY_HIGH)

        return wx.Bitmap(image)
