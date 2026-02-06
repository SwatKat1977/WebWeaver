
import wx
from image_helpers import ImageHelpers
from resources.webweaver_main_logo import WEBWEAVER_MAIN_LOGO

class StudioSplashScreen(wx.Frame):
    def __init__(self, core_version: str, studio_version: str):
        super().__init__(
            parent=None,
            title="",
            style=wx.FRAME_NO_TASKBAR | wx.BORDER_NONE | wx.STAY_ON_TOP
        )

        outer = wx.Panel(self)
        # Subtle gray border
        outer.SetBackgroundColour("#AAAAAA")
        panel = wx.Panel(outer)
        panel.SetBackgroundColour("#E8E8E8")
        outer_sizer = wx.BoxSizer(wx.VERTICAL)
        outer_sizer.Add(panel, 1, wx.ALL | wx.EXPAND, 2) # 2px border
        outer.SetSizer(outer_sizer)

        logo_bitmap = ImageHelpers.image_to_wxbitmap(WEBWEAVER_MAIN_LOGO)
        logo = wx.StaticBitmap(panel, bitmap=logo_bitmap)

        core = wx.StaticText(panel, label=f"Core: {core_version}")
        studio = wx.StaticText(panel, label=f"Studio: {studio_version}")

        core.SetForegroundColour("#aaaaaa")
        studio.SetForegroundColour("#aaaaaa")

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.AddStretchSpacer()
        sizer.Add(logo, 0, wx.ALIGN_CENTER | wx.ALL, 10)

        bottom_sizer = wx.BoxSizer(wx.HORIZONTAL)
        bottom_sizer.AddStretchSpacer()
        bottom_sizer.Add(core, 0, wx.RIGHT, 10)
        bottom_sizer.Add(studio, 0, wx.RIGHT, 10)

        sizer.Add(bottom_sizer, 0, wx.EXPAND | wx.BOTTOM, 8)
        sizer.AddStretchSpacer()

        panel.SetSizer(sizer)

        self.SetSize((700, 450))
        self.Centre()
