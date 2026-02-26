import wx
import io
from webweaver.studio.resources.webweaver_main_logo import WEBWEAVER_MAIN_LOGO
from webweaver.studio.version import __version__


class AboutDialog(wx.Dialog):
    def __init__(self, parent):
        super().__init__(
            parent,
            title="About WebWeaver Studio",
            style=wx.DEFAULT_DIALOG_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX)
        )

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
