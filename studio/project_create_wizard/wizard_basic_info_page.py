"""
This source file is part of Web Weaver
For the latest info, see https://github.com/SwatKat1977/WebWeaver

Copyright 2025 SwatKat1977

    This program is free software : you can redistribute it and /or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.If not, see < https://www.gnu.org/licenses/>.
"""
import wx
from wizard_step_indicator import WizardStepIndicator


class WizardBasicInfoPage(wx.Dialog):
    def __init__(self, parent, data):
        super().__init__(parent, title="Create your new solution",
                         style=wx.DEFAULT_DIALOG_STYLE)

        self.data = data  # shared dict

        main = wx.BoxSizer(wx.VERTICAL)

        self.steps = [
            "Basic solution info",
            "Browser selection",
            "Configure behaviour",
            "Finish",
        ]

        self.current_index = 0
        step_indicator = WizardStepIndicator(self, self.steps, active_index=0)
        main.Add(step_indicator, 0, wx.EXPAND | wx.ALL, 10)

        # Header
        header = wx.BoxSizer(wx.HORIZONTAL)
        icon = wx.StaticBitmap(self, bitmap=wx.ArtProvider.GetBitmap(
            wx.ART_TIP, wx.ART_OTHER, (32, 32)))
        header.Add(icon, 0, wx.ALL, 10)

        text_box = wx.BoxSizer(wx.VERTICAL)
        title = wx.StaticText(self, label="Create your new solution")
        title.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT,
                              wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        subtitle = wx.StaticText(
            self, label="Define basic information for your first solution.")
        subtitle.SetForegroundColour(wx.Colour(100, 100, 100))
        text_box.Add(title, 0)
        text_box.Add(subtitle, 0, wx.TOP, 4)

        header.Add(text_box, 1, wx.ALIGN_CENTER_VERTICAL)
        main.Add(header, 0, wx.LEFT | wx.RIGHT, 10)

        # Form
        form_panel = wx.Panel(self)
        form = wx.FlexGridSizer(0, 3, 8, 8)
        form.AddGrowableCol(1, 1)

        form.Add(wx.StaticText(form_panel, label="Solution name:"),
                 0, wx.ALIGN_CENTER_VERTICAL)
        self.txt_solution_name = wx.TextCtrl(form_panel)
        form.Add(self.txt_solution_name, 1, wx.EXPAND)
        form.Add((0, 0))

        form.Add(wx.StaticText(form_panel, label="Location:"),
                 0, wx.ALIGN_CENTER_VERTICAL)
        self.txt_solution_dir = wx.TextCtrl(form_panel)
        form.Add(self.txt_solution_dir, 1, wx.EXPAND)

        btn_browse = wx.Button(form_panel, label="…")
        btn_browse.SetMinSize((32, -1))
        btn_browse.Bind(wx.EVT_BUTTON, self.__on_browse)
        form.Add(btn_browse)

        form_panel.SetSizer(form)
        main.Add(form_panel, 0, wx.EXPAND | wx.ALL, 10)

        # Checkbox
        self.chk_dir = wx.CheckBox(self, label="Create directory for solution")
        self.chk_dir.SetValue(True)
        main.Add(self.chk_dir, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)

        # Button bar
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        btn_sizer.AddStretchSpacer()

        self.btn_cancel = wx.Button(self, wx.ID_CANCEL, "Cancel")
        self.btn_cancel.Bind(wx.EVT_BUTTON, lambda e: self.EndModal(wx.ID_CANCEL))
        btn_sizer.Add(self.btn_cancel, 0, wx.RIGHT, 10)

        self.btn_next = wx.Button(self, wx.ID_OK, "Next")
        self.btn_next.Bind(wx.EVT_BUTTON, self.__on_next)
        btn_sizer.Add(self.btn_next, 0)

        main.Add(btn_sizer, 0, wx.EXPAND | wx.ALL, 10)

        self.SetSizerAndFit(main)
        self.CentreOnParent()

    def on_browse(self, _evt):
        with wx.DirDialog(self, "Choose solution location") as dlg:
            if dlg.ShowModal() == wx.ID_OK:
                self.txt_location.SetValue(dlg.GetPath())

    def __validate(self) -> bool:
        name = self.txt_solution_name.GetValue().strip()
        if not name:
            wx.MessageBox("Please enter a solution name.",
                          "Validation error", wx.ICON_WARNING)
            return False

        solution_dir = self.txt_solution_dir.GetValue().strip()
        if not solution_dir:
            wx.MessageBox("Please enter a solution location.",
                          "Validation error", wx.ICON_WARNING)
            return False

        return True

    def __on_next(self, _event):
        if not self.__validate():
            return

        self.data["solution_name"] = self.txt_solution_name.GetValue().strip()
        self.data["solution_dir"] = self.txt_solution_dir.GetValue().strip()
        self.data["create_solution_dir"] = self.chk_dir.GetValue()

        self.EndModal(wx.ID_OK)
