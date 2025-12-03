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
from wizard_base_page import WizardBasePage


class WizardBasicInfoPage(WizardBasePage):
    def __init__(self, parent, wizard):
        super().__init__(
            parent,
            wizard,
            title="Create your new solution",
            subtitle="Define basic information for your first solution.",
        )

        main = wx.BoxSizer(wx.VERTICAL)

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

        form_panel.SetSizer(form)
        main.Add(form_panel, 0, wx.EXPAND | wx.ALL, 10)

        # Checkbox
        self.chk_directory = wx.CheckBox(self, label="Create directory for solution")
        self.chk_directory.SetValue(True)
        main.Add(self.chk_directory, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)

        self.SetSizer(main)

    def on_browse(self, _event):
        dlg = wx.DirDialog(self, "Choose solution location")
        if dlg.ShowModal() == wx.ID_OK:
            self.location.SetValue(dlg.GetPath())
        dlg.Destroy()

    def validate(self) -> bool:
        name = self.solution_name.GetValue().strip()
        if not name:
            wx.MessageBox("Please enter a solution name.",
                          "Validation error", wx.ICON_WARNING)
            return False

        # You can stash values in wizard.shared_data
        self.wizard.shared_data["solution_name"] = name
        self.wizard.shared_data["location"] = self.location.GetValue().strip()
        self.wizard.shared_data["create_dir"] = self.chk_directory.GetValue()
        return True
