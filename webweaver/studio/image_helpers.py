from io import BytesIO
import typing
import wx


class ImageHelpers:

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
