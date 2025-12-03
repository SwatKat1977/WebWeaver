import wx
import wx.adv


class StepIndicator(wx.Panel):
    """Small 4-step indicator bar like Ranorex."""
    def __init__(self, parent, active_index=0):
        super().__init__(parent)

        steps = ["Basic data", "Select browser", "Configure behavior", "Finish"]

        sizer = wx.BoxSizer(wx.HORIZONTAL)

        for i, label in enumerate(steps):
            circle_color = "#4CAF50" if i == active_index else "#CCCCCC"
            text_color = "#000000" if i == active_index else "#777777"

            circle = wx.Panel(self, size=(12, 12))
            circle.SetBackgroundColour(circle_color)
            circle.SetWindowStyle(wx.BORDER_NONE)

            circle.SetMinSize((12, 12))
            circle.SetMaxSize((12, 12))
            circle.SetBackgroundColour(circle_color)

            circle.SetForegroundColour(circle_color)
            circle.SetWindowStyle(wx.BORDER_NONE)

            # Round shape
            circle.Bind(wx.EVT_PAINT, lambda evt, c=circle, col=circle_color: self.draw_circle(evt, c, col))

            sizer.Add(circle, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 6)

            text = wx.StaticText(self, label=label)
            text.SetForegroundColour(text_color)
            sizer.Add(text, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 20)

        self.SetSizer(sizer)

    def draw_circle(self, evt, panel, color):
        dc = wx.PaintDC(panel)
        dc.SetBrush(wx.Brush(color))
        dc.SetPen(wx.Pen(color))
        w, h = panel.GetSize()
        dc.DrawCircle(w // 2, h // 2, min(w, h) // 2)


class NewSolutionDialog(wx.Dialog):
    def __init__(self, parent):
        super().__init__(
            parent,
            title="Create your new solution",
            style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER
        )

        main = wx.BoxSizer(wx.VERTICAL)

        # -----------------------------------
        # STEP INDICATOR (top)
        # -----------------------------------
        step = StepIndicator(self, active_index=0)
        main.Add(step, 0, wx.EXPAND | wx.ALL, 10)

        # -----------------------------------
        # HEADER SECTION
        # -----------------------------------
        header_sizer = wx.BoxSizer(wx.HORIZONTAL)

        rocket_icon = wx.ArtProvider.GetBitmap(wx.ART_TIP, wx.ART_OTHER, (48, 48))
        header_sizer.Add(wx.StaticBitmap(self, bitmap=rocket_icon), 0, wx.ALL, 10)

        title_sizer = wx.BoxSizer(wx.VERTICAL)

        lbl_title = wx.StaticText(self, label="Create your new solution")
        lbl_title.SetFont(wx.Font(15, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))

        lbl_sub = wx.StaticText(self, label="Define basic information for your first solution.")
        lbl_sub.SetForegroundColour("#666666")

        title_sizer.Add(lbl_title, 0)
        title_sizer.Add(lbl_sub, 0, wx.TOP, 4)

        header_sizer.Add(title_sizer, 1, wx.ALIGN_CENTER_VERTICAL)
        main.Add(header_sizer, 0, wx.LEFT | wx.RIGHT, 10)

        # -----------------------------------
        # FORM PANEL
        # -----------------------------------
        form_panel = wx.Panel(self)
        form = wx.FlexGridSizer(0, 3, 12, 10)
        form.AddGrowableCol(1, 1)

        # Solution name
        form.Add(wx.StaticText(form_panel, label="Solution name:"), 0, wx.ALIGN_CENTER_VERTICAL)
        self.solution_name = wx.TextCtrl(form_panel)
        form.Add(self.solution_name, 1, wx.EXPAND)
        form.Add((0, 0))

        # Location
        form.Add(wx.StaticText(form_panel, label="Location:"), 0, wx.ALIGN_CENTER_VERTICAL)
        self.location = wx.TextCtrl(form_panel)
        form.Add(self.location, 1, wx.EXPAND)

        browse = wx.Button(form_panel, label="…")
        browse.SetMinSize((32, -1))
        browse.Bind(wx.EVT_BUTTON, self.on_browse)
        form.Add(browse)

        # Project name
        form.Add(wx.StaticText(form_panel, label="Project name:"), 0, wx.ALIGN_CENTER_VERTICAL)
        self.project_name = wx.TextCtrl(form_panel)
        form.Add(self.project_name, 1, wx.EXPAND)
        form.Add((0, 0))

        form_panel.SetSizer(form)
        main.Add(form_panel, 0, wx.EXPAND | wx.ALL, 20)

        # -----------------------------------
        # CHECKBOXES
        # -----------------------------------
        self.chk_directory = wx.CheckBox(self, label="Create directory for solution")
        self.chk_directory.SetValue(True)

        main.Add(self.chk_directory, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)

        # -----------------------------------
        # BUTTON BAR
        # -----------------------------------
        btns = wx.BoxSizer(wx.HORIZONTAL)
        btns.AddStretchSpacer()

        btn_back = wx.Button(self, label="Back")
        btn_back.Bind(wx.EVT_BUTTON, lambda e: self.EndModal(wx.ID_CANCEL))
        btns.Add(btn_back, 0, wx.RIGHT, 10)

        btn_continue = wx.Button(self, label="Continue")
        btn_continue.Bind(wx.EVT_BUTTON, lambda e: self.EndModal(wx.ID_OK))
        btns.Add(btn_continue, 0)

        main.Add(btns, 0, wx.EXPAND | wx.ALL, 15)

        self.SetSizerAndFit(main)
        self.Centre()

    # -----------------------------------
    def on_browse(self, event):
        dlg = wx.DirDialog(self, "Choose solution location")
        if dlg.ShowModal() == wx.ID_OK:
            self.location.SetValue(dlg.GetPath())
        dlg.Destroy()


# ---------------------------------------------------------
# TEST LAUNCHER
# ---------------------------------------------------------
class MainFrame(wx.Frame):
    def __init__(self):
        super().__init__(None, title="Demo")
        btn = wx.Button(self, label="New Solution Wizard")
        btn.Bind(wx.EVT_BUTTON, self.show_dialog)
        self.Show()

    def show_dialog(self, _):
        dlg = NewSolutionDialog(self)
        dlg.ShowModal()
        dlg.Destroy()


if __name__ == "__main__":
    app = wx.App(False)
    MainFrame()
    app.MainLoop()
