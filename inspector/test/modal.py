import wx
import wx.adv


class NewSolutionDialog(wx.Dialog):
    def __init__(self, parent):
        super().__init__(
            parent,
            title="Create your new solution",
            style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER
        )

        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # -----------------------------
        # Header (icon + title text)
        # -----------------------------
        header_sizer = wx.BoxSizer(wx.HORIZONTAL)

        rocket_icon = wx.ArtProvider.GetBitmap(wx.ART_NEW_DIR, wx.ART_OTHER, (48,48))
        header_bitmap = wx.StaticBitmap(self, bitmap=rocket_icon)

        header_text = wx.StaticText(self,
            label="Create your new solution"
        )
        header_text.SetFont(wx.Font(14, wx.FONTFAMILY_DEFAULT,
                                    wx.FONTSTYLE_NORMAL,
                                    wx.FONTWEIGHT_BOLD))

        header_sizer.Add(header_bitmap, 0, wx.ALL, 10)
        header_sizer.Add(header_text, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 10)
        main_sizer.Add(header_sizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)

        # =============================
        # FORM PANEL
        # =============================
        form_panel = wx.Panel(self)
        form_sizer = wx.FlexGridSizer(0, 3, 12, 10)
        form_sizer.AddGrowableCol(1, 1)

        # --- Solution Name ---
        form_sizer.Add(wx.StaticText(form_panel, label="Solution name:"), 0, wx.ALIGN_CENTER_VERTICAL)
        self.solution_name = wx.TextCtrl(form_panel)
        form_sizer.Add(self.solution_name, 1, wx.EXPAND)

        form_sizer.Add((0,0))  # empty spacer cell

        # --- Location ---
        form_sizer.Add(wx.StaticText(form_panel, label="Location:"), 0, wx.ALIGN_CENTER_VERTICAL)

        self.location = wx.TextCtrl(form_panel)
        form_sizer.Add(self.location, 1, wx.EXPAND)

        browse_btn = wx.Button(form_panel, label="...")
        browse_btn.SetMinSize((32, -1))
        browse_btn.Bind(wx.EVT_BUTTON, self.on_browse)
        form_sizer.Add(browse_btn)

        # --- Project name ---
        form_sizer.Add(wx.StaticText(form_panel, label="Project name:"), 0, wx.ALIGN_CENTER_VERTICAL)
        self.project_name = wx.TextCtrl(form_panel)
        form_sizer.Add(self.project_name, 1, wx.EXPAND)
        form_sizer.Add((0,0))

        # Add form to panel
        form_panel.SetSizer(form_sizer)
        main_sizer.Add(form_panel, 0, wx.EXPAND | wx.ALL, 20)

        # =============================
        # CHECKBOXES
        # =============================
        self.chk_directory = wx.CheckBox(self, label="Create directory for solution")
        self.chk_directory.SetValue(True)

        main_sizer.Add(self.chk_directory, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 15)

        # =============================
        # BUTTON BAR
        # =============================
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.btn_back = wx.Button(self, label="Back")
        self.btn_continue = wx.Button(self, label="Continue")

        self.btn_back.Bind(wx.EVT_BUTTON, lambda e: self.EndModal(wx.ID_CANCEL))
        self.btn_continue.Bind(wx.EVT_BUTTON, lambda e: self.EndModal(wx.ID_OK))

        btn_sizer.AddStretchSpacer(1)
        btn_sizer.Add(self.btn_back, 0, wx.RIGHT, 10)
        btn_sizer.Add(self.btn_continue, 0)

        main_sizer.Add(btn_sizer, 0, wx.EXPAND | wx.ALL, 15)

        self.SetSizerAndFit(main_sizer)
        self.Layout()
        self.Centre()

    # -----------------------------------
    # Folder picker button action
    # -----------------------------------
    def on_browse(self, event):
        dlg = wx.DirDialog(self, "Choose solution location")
        if dlg.ShowModal() == wx.ID_OK:
            self.location.SetValue(dlg.GetPath())
        dlg.Destroy()


# ====================================================
# Example showing how to open the dialog
# ====================================================
class MainFrame(wx.Frame):
    def __init__(self):
        super().__init__(None, title="Demo")
        btn = wx.Button(self, label="New Solution Dialog")
        btn.Bind(wx.EVT_BUTTON, self.show_dialog)
        self.Show()

    def show_dialog(self, _event):
        dlg = NewSolutionDialog(self)
        result = dlg.ShowModal()

        if result == wx.ID_OK:
            print("Solution:", dlg.solution_name.GetValue())
            print("Location:", dlg.location.GetValue())
            print("Project:", dlg.project_name.GetValue())
            print("Create dir:", dlg.chk_directory.GetValue())
            print("Source control:", dlg.chk_source_control.GetValue())

        dlg.Destroy()


if __name__ == "__main__":
    app = wx.App(False)
    MainFrame()
    app.MainLoop()
