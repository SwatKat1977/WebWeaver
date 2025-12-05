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
from project_create_wizard.wizard_ids import ID_BACK_BUTTON


class WizardFinishPage(wx.Dialog):

    def __init__(self, parent, data):
        super().__init__(parent, title="Set up your web test",
                         style=wx.DEFAULT_DIALOG_STYLE)

        self.data = data
        main = wx.BoxSizer(wx.VERTICAL)

        self.steps = [
            "Basic solution info",
            "Browser selection",
            "Configure behaviour",
            "Finish",
        ]

        self.current_index = 0
        step_indicator = WizardStepIndicator(self, self.steps, active_index=1)
        main.Add(step_indicator, 0, wx.EXPAND | wx.ALL, 10)

        # Header
        header = wx.BoxSizer(wx.HORIZONTAL)
        icon = wx.StaticBitmap(self, bitmap=wx.ArtProvider.GetBitmap(
            wx.ART_TIP, wx.ART_OTHER, (32, 32)))
        header.Add(icon, 0, wx.ALL, 10)

        text_box = wx.BoxSizer(wx.VERTICAL)
        title = wx.StaticText(self, label="Almost there")
        title.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT,
                              wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        subtitle = wx.StaticText(
            self, label=("Read what's next and then click Finish to create "
                         "your solution and get started."))
        subtitle.SetForegroundColour(wx.Colour(100, 100, 100))
        text_box.Add(title, 0)
        text_box.Add(subtitle, 0, wx.TOP, 4)

        header.Add(text_box, 1, wx.ALIGN_CENTER_VERTICAL)
        main.Add(header, 0, wx.LEFT | wx.RIGHT, 10)

        # Button bar
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        btn_sizer.AddStretchSpacer()

        self.btn_cancel = wx.Button(self, wx.ID_CANCEL, "Cancel")
        self.btn_cancel.Bind(wx.EVT_BUTTON, lambda e: self.EndModal(wx.ID_CANCEL))
        btn_sizer.Add(self.btn_cancel, 0, wx.RIGHT, 10)

        btn_back = wx.Button(self, ID_BACK_BUTTON, "Back")
        btn_back.Bind(wx.EVT_BUTTON, lambda e: self.EndModal(ID_BACK_BUTTON))
        btn_sizer.Add(btn_back, 0, wx.RIGHT, 10)

        self.btn_next = wx.Button(self, wx.ID_OK, "Finish")
        self.btn_next.Bind(wx.EVT_BUTTON, self.__on_next)
        btn_sizer.Add(self.btn_next, 0)

        main.Add(btn_sizer, 0, wx.EXPAND | wx.ALL, 10)

        self.SetSizerAndFit(main)
        self.CentreOnParent()

    def __on_next(self, _event):
        self.EndModal(wx.ID_OK)
