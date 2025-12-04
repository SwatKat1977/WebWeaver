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
from project_create_wizard.wizard_basic_info_page import WizardBasicInfoPage
from project_create_wizard.wizard_web_select_browser_page import WizardWebSelectBrowserPage


class ProjectCreateWizardDialog(wx.Dialog):
    def __init__(self, parent):
        super().__init__(
            parent,
            title="Create your new solution",
            style=wx.DEFAULT_DIALOG_STYLE
        )

        # Place to store data between pages
        self.shared_data = {}

        self.steps = [
            "Basic solution info",
            "Browser selection",
            "Configure behaviour",
            "Finish",
        ]

        self.current_index = 0
        self.pages: list[WizardBasePage] = []

        main = wx.BoxSizer(wx.VERTICAL)

        # Step indicator
        self.step_indicator = WizardStepIndicator(self, self.steps, active_index=0)
        main.Add(self.step_indicator, 0, wx.EXPAND | wx.ALL, 10)

        # Header (icon + title + subtitle)
        header_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.header_icon = wx.StaticBitmap(
            self,
            bitmap=wx.ArtProvider.GetBitmap(wx.ART_TIP, wx.ART_OTHER, (48, 48)),
        )
        header_sizer.Add(self.header_icon, 0, wx.ALL, 10)

        title_box = wx.BoxSizer(wx.VERTICAL)
        self.lbl_title = wx.StaticText(self, label="")
        self.lbl_title.SetFont(wx.Font(
            15,
            wx.FONTFAMILY_DEFAULT,
            wx.FONTSTYLE_NORMAL,
            wx.FONTWEIGHT_BOLD,
        ))

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
        main.Add(self.page_container, 0, wx.EXPAND | wx.ALL, 10)

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

        # ---- Create all pages, compute max size, then show first page ----
        self.pages = [
            WizardBasicInfoPage(self.page_container, self),
            WizardWebSelectBrowserPage(self.page_container, self),
        ]

        # Compute max required size for the page container
        max_w = 0
        max_h = 0
        for page in self.pages:
            page.Layout()
            sizer = page.GetSizer()
            if sizer:
                size = sizer.CalcMin()
            else:
                size = page.GetEffectiveMinSize()
            max_w = max(max_w, size.width)
            max_h = max(max_h, size.height)

        # Fix the page_container so it’s always big enough for any page
        self.page_container.SetMinSize((max_w, max_h))

        # Show page 0 in the container
        for p in self.pages:
            p.Hide()
        self.page_sizer.Add(self.pages[0], 1, wx.EXPAND)
        self.pages[0].Show()

        # Set header text for page 0
        self.step_indicator.set_active(0)
        self.lbl_title.SetLabel(self.pages[0].title)
        self.lbl_subtitle.SetLabel(self.pages[0].subtitle)

        # Back button hidden on first page
        self.btn_back.Hide()

        # Now size the whole dialog once, based on the largest page
        self.Layout()
        self.Fit()
        self.CentreOnScreen()

    def create_pages(self):
        self.pages = [
            WizardBasicInfoPage(self.page_container, self),
            WizardWebSelectBrowserPage(self.page_container, self)
        ]

    def show_page(self, index: int):
        if index < 0 or index >= len(self.pages):
            return

        if 0 <= self.current_index < len(self.pages):
            self.pages[self.current_index].on_leave()

        self.current_index = index
        page = self.pages[index]

        # Update step indicator + header text
        self.step_indicator.set_active(index)
        self.lbl_title.SetLabel(page.title)
        self.lbl_subtitle.SetLabel(page.subtitle)

        # Swap page in container (size is already guaranteed big enough)
        self.page_sizer.Clear(delete_windows=False)
        for p in self.pages:
            p.Hide()
        page.Show()
        self.page_sizer.Add(page, 1, wx.EXPAND)

        self.page_container.Layout()
        self.Layout()

        # Update next/back labels & visibility
        self.btn_back.Show(index > 0)
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
