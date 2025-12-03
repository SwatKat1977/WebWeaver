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


class ProjectCreateWizardDialog(wx.Dialog):
    def __init__(self, parent):
        super().__init__(
            parent,
            title="Create your new solution",
            style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER,
        )

        self.shared_data = {}  # place to store data between pages

        self.steps = [
            "Basic data",
            "Web application",
            "Configure behaviour",
            "Finish",
        ]

        self.current_index = 0
        self.pages = []

        main = wx.BoxSizer(wx.VERTICAL)

        # Step indicator
        self.step_indicator = WizardStepIndicator(self,
                                                  self.steps,
                                                  active_index=0)
        main.Add(self.step_indicator, 0, wx.EXPAND | wx.ALL, 10)

        # Header (icon + title + subtitle)
        header_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.header_icon = wx.StaticBitmap(
            self,
            bitmap=wx.ArtProvider.GetBitmap(wx.ART_TIP,
                                            wx.ART_OTHER,
                                            (48, 48)),
        )
        header_sizer.Add(self.header_icon, 0, wx.ALL, 10)

        title_box = wx.BoxSizer(wx.VERTICAL)
        self.lbl_title = wx.StaticText(self, label="")
        self.lbl_title.SetFont(wx.Font(15,
                                       wx.FONTFAMILY_DEFAULT,
                                       wx.FONTSTYLE_NORMAL,
                                       wx.FONTWEIGHT_BOLD))

        self.lbl_subtitle = wx.StaticText(self, label="")
        self.lbl_subtitle.SetForegroundColour(wx.Colour(100, 100, 100))

        title_box.Add(self.lbl_title, 0)
        title_box.Add(self.lbl_subtitle, 0, wx.TOP, 4)
        header_sizer.Add(title_box, 1, wx.ALIGN_CENTER_VERTICAL)

        main.Add(header_sizer, 0, wx.LEFT | wx.RIGHT, 10)

        # Page container
        self.page_container = wx.Panel(self)
        self.page_sizer = wx.BoxSizer(wx.VERTICAL)
        self.page_container.SetSizer(self.page_sizer)
        main.Add(self.page_container, 1, wx.EXPAND | wx.ALL, 10)

        # Button bar
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        btn_sizer.AddStretchSpacer()

        self.btn_cancel = wx.Button(self, label="Cancel")
        self.btn_cancel.Bind(wx.EVT_BUTTON, self.on_cancel)
        btn_sizer.Add(self.btn_cancel, 0, wx.RIGHT, 10)

        self.btn_back = wx.Button(self, label="Back")
        self.btn_back.Bind(wx.EVT_BUTTON, self.on_back)
        btn_sizer.Add(self.btn_back, 0, wx.RIGHT, 10)

        self.btn_next = wx.Button(self, label="Next")
        self.btn_next.Bind(wx.EVT_BUTTON, self.on_next)
        btn_sizer.Add(self.btn_next, 0)

        main.Add(btn_sizer, 0, wx.EXPAND | wx.ALL, 10)

        self.SetSizer(main)

        # Create pages
        self.create_pages()
        self.show_page(0)

        self.SetSizerAndFit(main)
        self.Layout()
        self.CentreOnScreen()

    def create_pages(self):
        self.pages = [
            BasicDataPage(self.page_container, self),
            WebTestPage(self.page_container, self),
            # You can add more pages here later...
        ]

    def show_page(self, index: int):
        if index < 0 or index >= len(self.pages):
            return

        # Leave old page
        if 0 <= self.current_index < len(self.pages):
            old_page = self.pages[self.current_index]
            old_page.on_leave()

        self.current_index = index
        page = self.pages[index]

        # Update step indicator + header text
        self.step_indicator.SetActive(index)
        self.lbl_title.SetLabel(page.get_title())
        self.lbl_subtitle.SetLabel(page.get_subtitle())

        # Swap page in container
        self.page_sizer.Clear(delete_windows=False)
        for p in self.pages:
            p.Hide()
        page.Show()
        self.page_sizer.Add(page, 1, wx.EXPAND)
        self.page_container.Layout()

        # Update buttons
        self.btn_back.Enable(index > 0)
        if index == len(self.pages) - 1:
            self.btn_next.SetLabel("Finish")
        else:
            self.btn_next.SetLabel("Next")

        page.on_enter()

    def on_cancel(self, _event):
        self.EndModal(wx.ID_CANCEL)

    def on_back(self, _event):
        if self.current_index > 0:
            self.show_page(self.current_index - 1)

    def on_next(self, _event):
        page = self.pages[self.current_index]
        if not page.validate():
            return

        if self.current_index == len(self.pages) - 1:
            # Finish
            self.EndModal(wx.ID_OK)
        else:
            self.show_page(self.current_index + 1)
