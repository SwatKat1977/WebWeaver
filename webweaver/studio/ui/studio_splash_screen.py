
import wx
from ..image_helpers import ImageHelpers
from ..resources.webweaver_main_logo import WEBWEAVER_MAIN_LOGO

class StudioSplashScreen(wx.Frame):
    def __init__(self, core_version: str, studio_version: str):
        super().__init__(
            parent=None,
            title="",
            style=wx.FRAME_NO_TASKBAR | wx.BORDER_NONE | wx.STAY_ON_TOP
        )

        self.main_frame = None

        outer = wx.Panel(self)
        # Subtle gray border
        outer.SetBackgroundColour("#AAAAAA")

        frame_sizer = wx.BoxSizer(wx.VERTICAL)
        frame_sizer.Add(outer, 1, wx.EXPAND)
        self.SetSizer(frame_sizer)

        panel = wx.Panel(outer)
        panel.SetBackgroundColour("#E8E8E8")
        outer_sizer = wx.BoxSizer(wx.VERTICAL)
        outer_sizer.Add(panel, 1, wx.ALL | wx.EXPAND, 2) # 2px border
        outer.SetSizer(outer_sizer)

        logo_bitmap = ImageHelpers.image_to_wxbitmap(WEBWEAVER_MAIN_LOGO,
                                                     width=500,
                                                     height=500)

        logo = wx.StaticBitmap(panel, bitmap=logo_bitmap)

        core = wx.StaticText(panel, label=f"Core: {core_version}")
        studio = wx.StaticText(panel, label=f"Studio: {studio_version}")

        core.SetForegroundColour("#000000")
        studio.SetForegroundColour("#000000")

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(logo, 0, wx.ALIGN_CENTER | wx.ALL, 10)
        sizer.AddStretchSpacer()

        bottom_sizer = wx.BoxSizer(wx.HORIZONTAL)
        bottom_sizer.AddStretchSpacer()
        bottom_sizer.Add(core, 0, wx.RIGHT, 10)
        bottom_sizer.Add(studio, 0, wx.RIGHT, 10)

        sizer.Add(bottom_sizer, 0, wx.EXPAND | wx.BOTTOM, 8)

        panel.SetSizer(sizer)

        panel.Layout()
        outer.Layout()
        self.Layout()

        self.SetSize((700, 550))
        self.Centre()

        # Start a simple one-shot timer
        self._timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self._on_timer, self._timer)
        self._timer.StartOnce(5000)

    def set_main_frame(self, frame):
        self.main_frame = frame

    def _on_timer(self, _event):
        if self.main_frame:
            self.main_frame.Show()
            wx.CallAfter(self.main_frame.init_aui)

        self.Destroy()
