"""
This source file is part of Web Weaver
For the latest info, see https://github.com/SwatKat1977/WebWeaver

Copyright 2025-2026 Webweaver Development Team

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
import wx
from solution_create_wizard.solution_create_wizard_data import \
    SolutionCreateWizardData
from wizard_step_indicator import WizardStepIndicator
from solution_create_wizard.solution_widget_ids import \
    SOLUTION_WIZARD_BACK_BUTTON_ID


class WizardFinishPage(wx.Dialog):
    NEXT_WIZARD_PAGE = None

    def __init__(self, parent: wx.Window, data: SolutionCreateWizardData,
                 steps: list):
        super().__init__(parent, title="Set up your web test",
                         style=wx.DEFAULT_DIALOG_STYLE)
        self._data: SolutionCreateWizardData = data
        self._steps: list = steps

        main_sizer: wx.BoxSizer =  wx.BoxSizer(wx.VERTICAL)

        step_indicator: WizardStepIndicator = WizardStepIndicator(
            self, self._steps, 3)
        main_sizer.Add(step_indicator, 0, wx.EXPAND | wx.ALL, 10)

        # Header
        header_sizer: wx.BoxSizer = wx.BoxSizer(wx.HORIZONTAL)
        icon: wx.StaticBitmap = wx.StaticBitmap(
            self,
            wx.ID_ANY,
            wx.ArtProvider.GetBitmap(wx.ART_TIP,
                                     wx.ART_OTHER,
                                     wx.Size(32, 32)))
        header_sizer.Add(icon, 0, wx.ALL, 10)

        text_sizer: wx.BoxSizer = wx.BoxSizer(wx.VERTICAL)
        title: wx.StaticText = wx.StaticText(self, wx.ID_ANY, "Almost there")
        title.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT,
            wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        subtitle: wx.StaticText = wx.StaticText(
            self,
            wx.ID_ANY,
            "Read what's next and then click Finish to create "
            "your solution and get started.")
        subtitle.SetForegroundColour(wx.Colour(100, 100, 100))
        text_sizer.Add(title, 0)
        text_sizer.Add(subtitle, 0, wx.TOP, 4)

        header_sizer.Add(text_sizer, 1, wx.ALIGN_CENTER_VERTICAL)
        main_sizer.Add(header_sizer, 0, wx.LEFT | wx.RIGHT, 10)

        # Button bar
        button_bar_sizer: wx.BoxSizer = wx.BoxSizer(wx.HORIZONTAL)
        button_bar_sizer.AddStretchSpacer()

        btn_cancel: wx.Button =  wx.Button(self, wx.ID_CANCEL, "Cancel")
        btn_cancel.Bind(wx.EVT_BUTTON, lambda evt: self.EndModal(wx.ID_CANCEL))
        button_bar_sizer.Add(btn_cancel, 0, wx.RIGHT, 10)

        btn_back: wx.Button = wx.Button(self,
                                        SOLUTION_WIZARD_BACK_BUTTON_ID,
                                        "Back")
        btn_back.Bind(wx.EVT_BUTTON,
                      lambda evt: self.EndModal(SOLUTION_WIZARD_BACK_BUTTON_ID))
        button_bar_sizer.Add(btn_back, 0, wx.RIGHT, 10)

        btn_next: wx.Button = wx.Button(self, wx.ID_OK, "Finish")
        btn_next.Bind(wx.EVT_BUTTON, self._on_next_click_event)
        button_bar_sizer.Add(btn_next, 0)

        main_sizer.Add(button_bar_sizer, 0, wx.EXPAND | wx.ALL, 10)

        self.SetSizerAndFit(main_sizer)
        self.CentreOnParent()

    def _on_next_click_event(self, _event: wx.CommandEvent):
        self.EndModal(wx.ID_OK)
