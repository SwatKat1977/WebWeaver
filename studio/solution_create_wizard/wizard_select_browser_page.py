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
from solution_create_wizard.solution_creation_page import SolutionCreationPage
from solution_create_wizard.browser_logos import (
    load_browser_logo_chromium,
    load_browser_logo_firefox,
    load_browser_logo_google_chrome,
    load_browser_logo_microsoft_edge)
from solution_create_wizard.solution_widget_ids import \
    SOLUTION_WIZARD_BACK_BUTTON_ID


#include <wx/tglbtn.h>
#include "SolutionCreateWizard/SolutionCreateWizardBasePage.h"


class WizardSelectBrowserPage(wx.Dialog):
    DEFAULT_URL: str = "https://www.example.com"

    NEXT_WIZARD_PAGE = None

    def __init__(self, parent: wx.Window, data: SolutionCreateWizardData,
                 steps: list):
        super().__init__(parent, title="Set up your web test",
                         style=wx.DEFAULT_DIALOG_STYLE)
        self._data: SolutionCreateWizardData = data
        self._steps: list = steps
        self._browser_buttons = []

        main_sizer: wx.BoxSizer = wx.BoxSizer(wx.VERTICAL)

        # --- Step indicator ---
        step_indicator: WizardStepIndicator = WizardStepIndicator(self,
                                                                  self._steps,
                                                                  1)
        main_sizer.Add(step_indicator, 0, wx.EXPAND | wx.ALL, 10)

        # --- Header ---
        header_sizer: wx.BoxSizer = wx.BoxSizer(wx.HORIZONTAL)

        # --- Wizard page icon ---
        icon_bitmap: wx.Bitmap = wx.ArtProvider.GetBitmap(
            wx.ART_TIP, wx.ART_OTHER, wx.Size(32, 32))
        icon: wx.StaticBitmap = wx.StaticBitmap(self, wx.ID_ANY, icon_bitmap)
        header_sizer.Add(icon, 0, wx.ALL, 10)

        text_box: wx.BoxSizer = wx.BoxSizer(wx.VERTICAL)
        title: wx.StaticText = wx.StaticText(self,
                                             wx.ID_ANY,
                                             "Set up your web test")
        title.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT,
                      wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        subtitle: wx.StaticText = wx.StaticText(
            self, wx.ID_ANY, "Which web browser do you want to test on?")
        subtitle.SetForegroundColour(wx.Colour(100, 100, 100))
        text_box.Add(title, 0)
        text_box.Add(subtitle, 0, wx.TOP, 4)

        header_sizer.Add(text_box, 1, wx.ALIGN_CENTER_VERTICAL)
        main_sizer.Add(header_sizer, 0, wx.LEFT | wx.RIGHT, 10)

        # URL
        url_sizer: wx.BoxSizer = wx.BoxSizer(wx.VERTICAL)
        url_sizer.Add(wx.StaticText(self, wx.ID_ANY, "URL"), 0, wx.BOTTOM, 4)
        self._txt_base_url = wx.TextCtrl(self, wx.ID_ANY, self.DEFAULT_URL)
        url_sizer.Add(self._txt_base_url, 0, wx.EXPAND)
        main_sizer.Add(url_sizer, 0, wx.EXPAND | wx.ALL, 10)

        # Browser label + hint
        lbl_browser: wx.StaticText = wx.StaticText(
            self, wx.ID_ANY, "Select browser")
        lbl_browser.SetFont(wx.Font(10,
                                    wx.FONTFAMILY_DEFAULT,
                                    wx.FONTSTYLE_NORMAL,
                                    wx.FONTWEIGHT_BOLD))
        main_sizer.Add(lbl_browser, 0, wx.LEFT | wx.RIGHT, 10)

        hint: wx.StaticText = wx.StaticText(
            self, wx.ID_ANY,
            "The selected browser must be installed on this system.")
        hint.SetForegroundColour(wx.Colour(120, 120, 120))
        main_sizer.Add(hint, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)

        # Scrollable browser icons(simplified)
        scroll: wx.ScrolledWindow = wx.ScrolledWindow(
            self,
            wx.ID_ANY,
            wx.DefaultPosition,
            wx.DefaultSize,
            wx.HSCROLL | wx.BORDER_NONE)
        scroll.SetScrollRate(10, 0)
        scroll.SetMinSize(wx.Size(-1, 110))

        hsizer: wx.BoxSizer = wx.BoxSizer(wx.HORIZONTAL)

        # List of browsers
        browsers = [
            ("Chrome", load_browser_logo_google_chrome()),
            ("Chromium", load_browser_logo_chromium()),
            ("Edge (Chromium)", load_browser_logo_microsoft_edge()),
            ("Firefox", load_browser_logo_firefox())
        ]

        self._browser_buttons.clear()

        for name, bmp in browsers:
            col = wx.BoxSizer(wx.VERTICAL)
            btn = wx.BitmapToggleButton(scroll, wx.ID_ANY, bmp)

            label = wx.StaticText(scroll, wx.ID_ANY, name)
            label.SetForegroundColour(wx.Colour(80, 80, 80))

            col.Add(btn, 0, wx.ALIGN_CENTER | wx.BOTTOM, 4)
            col.Add(label, 0, wx.ALIGN_CENTER)
            hsizer.Add(col, 0, wx.RIGHT, 20)

            btn.Bind(wx.EVT_TOGGLEBUTTON, self._on_browser_toggle_event)
            self._browser_buttons.append((name, btn))

        scroll.SetSizer(hsizer)
        main_sizer.Add(scroll,
                       0,
                       wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM,
                       10)

        # Checkbox
        self._chk_launch_browser: wx.CheckBox = wx.CheckBox(
            self,
            wx.ID_ANY,
            "Launch browser automatically. Uncheck if browser is already running.")
        main_sizer.Add(self._chk_launch_browser,
                       0,
                       wx.LEFT | wx.RIGHT | wx.BOTTOM,
                       10)

        # Button bar
        button_bar_sizer: wx.BoxSizer = wx.BoxSizer(wx.HORIZONTAL)
        button_bar_sizer.AddStretchSpacer()

        btn_cancel: wx.Button = wx.Button(self, wx.ID_CANCEL, "Cancel")
        btn_cancel.Bind(wx.EVT_BUTTON, lambda evt: self.EndModal(wx.ID_CANCEL))
        button_bar_sizer.Add(btn_cancel, 0, wx.RIGHT, 10)

        btn_back: wx.Button = wx.Button(self,
                                        SOLUTION_WIZARD_BACK_BUTTON_ID,
                                        "Back")
        btn_back.Bind(wx.EVT_BUTTON,
                      lambda evt: self.EndModal(SOLUTION_WIZARD_BACK_BUTTON_ID))
        button_bar_sizer.Add(btn_back, 0, wx.RIGHT, 10)

        btn_next: wx.Button = wx.Button(self, wx.ID_OK, "Next")
        btn_next.Bind(wx.EVT_BUTTON, self._on_next_click_event)
        button_bar_sizer.Add(btn_next, 0)
        main_sizer.Add(button_bar_sizer, 0, wx.EXPAND | wx.ALL, 10)

        self.SetSizerAndFit(main_sizer)
        self.CentreOnParent()

    def _on_browser_toggle_event(self, event: wx.CommandEvent) -> None:
        """
            Ensure that only one browser toggle button can be active at a time.

            When a browser button is clicked, this handler deactivates all other
            buttons in ``browser_buttons`` to enforce exclusive selection.
        """
        clicked: wx.Window = event.GetEventObject()

        for name, btn in self._browser_buttons:
            if btn is not clicked:
                btn.SetValue(False)

        event.Skip()

    def _validate_fields(self) -> bool:
        """
        Validate the user's input before allowing the wizard to advance.

        This method checks that:
        * the URL field is not empty
        * a browser has been selected from the available toggle buttons

        If validation succeeds, the selected values are written to the
        wizard's shared data dictionary. If validation fails, a warning
        message is shown and the wizard remains on the current page.

        Returns
        -------
        bool
            True if the page is valid and the wizard may proceed; False if
            validation fails and navigation should be blocked.
        """
        base_url: str = self._txt_base_url.GetValue().strip()
        if not base_url:
            wx.MessageBox("Please enter a base URL.",
                          "Validation error",
                          wx.ICON_WARNING)
            return False

        selected_browser: str = ""
        for name, btn in self._browser_buttons:
            if btn.GetValue():
                selected_browser = name
                break

        if not selected_browser:
            wx.MessageBox("Please select a browser.",
                          "Missing information",
                          wx.ICON_WARNING)
            return False

        self._data.base_url = base_url
        self._data.browser = selected_browser
        self._data.launch_browser_automatically = \
            self._chk_launch_browser.GetValue()

        return True

    def _on_next_click_event(self, _event: wx.CommandEvent) -> None:
        if not self._validate_fields():
            return

        self.EndModal(wx.ID_OK)
