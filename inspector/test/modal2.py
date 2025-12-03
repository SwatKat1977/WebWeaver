import wx
from browser_icons import (bitmap_from_base64,
                           CHROMIUM_BROWSER_ICON,
                           CHROME_BROWSER_ICON,
                           FIREFOX_BROWSER_ICON,
                           MICROSOFT_EDGE_BROWSER_ICON)


class StepIndicator(wx.Panel):
    def __init__(self, parent, active_index=1):
        super().__init__(parent)
        steps = ["Basic data", "Web application", "Configure behavior", "Finish"]
        sizer = wx.BoxSizer(wx.HORIZONTAL)

        for i, label in enumerate(steps):
            circle_color = "#4CAF50" if i == active_index else "#CCCCCC"
            text_color = "#000000" if i == active_index else "#999999"

            circle = wx.Panel(self, size=(12, 12))
            circle.SetBackgroundColour(self.GetBackgroundColour())
            circle.Bind(wx.EVT_PAINT,
                        lambda evt, p=circle, c=circle_color: self.draw_circle(evt, p, c))

            sizer.Add(circle, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 6)

            t = wx.StaticText(self, label=label)
            t.SetForegroundColour(text_color)
            sizer.Add(t, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 25)

        self.SetSizer(sizer)

    def draw_circle(self, evt, panel, color):
        dc = wx.PaintDC(panel)
        dc.SetBrush(wx.Brush(color))
        dc.SetPen(wx.Pen(color))
        w, h = panel.GetSize()
        dc.DrawCircle(w // 2, h // 2, min(w, h) // 2)


class WebTestSetupDialog(wx.Dialog):
    def __init__(self, parent):
        super().__init__(
            parent,
            title="Create your new solution",
            style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER
        )

        main = wx.BoxSizer(wx.VERTICAL)

        # --- Step Header ---
        main.Add(StepIndicator(self, active_index=1), 0, wx.EXPAND | wx.ALL, 10)

        # --- Header text ---
        header = wx.BoxSizer(wx.HORIZONTAL)
        icon = wx.ArtProvider.GetBitmap(wx.ART_TIP, wx.ART_OTHER, (48, 48))
        header.Add(wx.StaticBitmap(self, bitmap=icon), 0, wx.ALL, 10)

        text = wx.BoxSizer(wx.VERTICAL)
        title = wx.StaticText(self, label="Set up your web test")
        title.SetFont(wx.Font(15, wx.DEFAULT, wx.NORMAL, wx.BOLD))
        sub = wx.StaticText(
            self,
            label="Which web application do you want to test and on which browser?"
        )
        sub.SetForegroundColour("#777777")

        text.Add(title)
        text.Add(sub, 0, wx.TOP, 4)
        header.Add(text, 1, wx.ALIGN_CENTER_VERTICAL)

        main.Add(header, 0, wx.LEFT | wx.RIGHT, 10)

        # --- URL area ---
        url_section = wx.BoxSizer(wx.VERTICAL)
        url_section.Add(wx.StaticText(self, label="URL"), 0, wx.BOTTOM, 4)
        self.url = wx.TextCtrl(self, value="https://www.ranorex.com")
        url_section.Add(self.url, 0, wx.EXPAND)
        main.Add(url_section, 0, wx.EXPAND | wx.ALL, 15)

        # --- Browser label ---
        lbl_browser = wx.StaticText(self, label="Select browser")
        lbl_browser.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD))
        main.Add(lbl_browser, 0, wx.LEFT | wx.RIGHT, 15)

        hint = wx.StaticText(self, label="The selected browser must be installed on this system.")
        hint.SetForegroundColour("#777777")
        main.Add(hint, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 15)

        # ---------------------------------------------------------------
        #   SCROLLABLE BROWSER LIST (just like Ranorex)
        # ---------------------------------------------------------------
        scroll = wx.ScrolledWindow(self, style=wx.HSCROLL | wx.VSCROLL)
        scroll.SetScrollRate(10, 10)

        browser_sizer = wx.BoxSizer(wx.HORIZONTAL)

        chromium_bmp = bitmap_from_base64(CHROMIUM_BROWSER_ICON)
        chrome_bmp = bitmap_from_base64(CHROME_BROWSER_ICON)
        firefox_bmp = bitmap_from_base64(FIREFOX_BROWSER_ICON)
        ms_edge_bmp = bitmap_from_base64(MICROSOFT_EDGE_BROWSER_ICON)

        # List of browsers
        browsers = [
            ("Firefox", firefox_bmp),
            ("Chrome", chrome_bmp),
            ("Chromium", chromium_bmp),
            ("Edge (Chromium)", ms_edge_bmp),
        ]

        self.browser_buttons = []

        for name, bitmap_entry in browsers:
            column = wx.BoxSizer(wx.VERTICAL)

            btn = wx.BitmapToggleButton(
                scroll,
                -1,
                bitmap_entry
            )

            label = wx.StaticText(scroll, label=name)
            label.SetForegroundColour("#555555")

            column.Add(btn, 0, wx.ALIGN_CENTER | wx.BOTTOM, 4)
            column.Add(label, 0, wx.ALIGN_CENTER)

            browser_sizer.Add(column, 0, wx.RIGHT, 25)

            btn.Bind(wx.EVT_TOGGLEBUTTON, self.on_browser_toggle)
            self.browser_buttons.append(btn)

        scroll.SetSizer(browser_sizer)
        scroll.SetMinSize((-1, 85))  # good height for icon + label
        main.Add(scroll, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 15)

        # --- Checkbox ---
        self.chk_launch = wx.CheckBox(
            self,
            label="Launch browser automatically. Uncheck if browser is already running."
        )
        main.Add(self.chk_launch, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 15)

        # --- Buttons ---
        buttons = wx.BoxSizer(wx.HORIZONTAL)
        buttons.AddStretchSpacer()
        back = wx.Button(self, label="Back")
        cont = wx.Button(self, label="Continue")
        back.Bind(wx.EVT_BUTTON, lambda e: self.EndModal(wx.ID_CANCEL))
        cont.Bind(wx.EVT_BUTTON, lambda e: self.EndModal(wx.ID_OK))

        buttons.Add(back, 0, wx.RIGHT, 10)
        buttons.Add(cont)
        main.Add(buttons, 0, wx.EXPAND | wx.ALL, 15)

        self.SetSizerAndFit(main)
        self.Centre()

    # --- Make selection exclusive ---
    def on_browser_toggle(self, event):
        clicked = event.GetEventObject()
        for b in self.browser_buttons:
            if b != clicked:
                b.SetValue(False)


# Test harness
class TestFrame(wx.Frame):
    def __init__(self):
        super().__init__(None, title="Scroll Demo")
        btn = wx.Button(self, label="Show Dialog")
        btn.Bind(wx.EVT_BUTTON, self.open_dialog)
        self.Show()

    def open_dialog(self, _):
        dlg = WebTestSetupDialog(self)
        dlg.ShowModal()
        dlg.Destroy()


if __name__ == "__main__":
    app = wx.App(False)
    TestFrame()
    app.MainLoop()
