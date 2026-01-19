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
from solution_create_wizard.solution_creation_page import SolutionCreationPage
from solution_create_wizard.browser_logos import (
    load_browser_logo_chromium,
    load_browser_logo_firefox,
    load_browser_logo_google_chrome,
    load_browser_logo_microsoft_edge)
from solution_create_wizard.solution_wizard_base import SolutionWizardBase


class WizardSelectBrowserPage(SolutionWizardBase):
    """
    Wizard page for selecting the target browser and base URL.

    This page allows the user to:
    - Enter the base URL for the web test
    - Select which browser to use for recording and playback
    - Choose whether the browser should be launched automatically

    The selected values are validated and written back into the shared
    SolutionCreateWizardData object before the wizard proceeds to the
    next step.
    """
    # pylint: disable=too-few-public-methods

    DEFAULT_URL: str = "https://www.example.com"

    TITLE_STR: str = "Set up your web test"
    SUBTITLE_STR: str = "Which web browser do you want to test on?"

    NEXT_WIZARD_PAGE = SolutionCreationPage.PAGE_NO_BEHAVIOUR_PAGE

    def __init__(self,
                 parent: wx.Window,
                 data: SolutionCreateWizardData):
        """
        Create the browser selection page of the solution creation wizard.

        This page presents controls for entering the base URL, choosing a target
        browser from the available options, and configuring whether the browser
        should be launched automatically.

        Args:
            parent (wx.Window): The parent window that owns this wizard page.
            data (SolutionCreateWizardData): Shared wizard data object used to
                store and retrieve information collected throughout the wizard.
        """
        super().__init__("Solution Wizard",
                         parent, data, 1)
        self._browser_buttons = []

        # --- Header ---
        self._create_header(self.TITLE_STR, self.SUBTITLE_STR)

        # URL
        url_sizer: wx.BoxSizer = wx.BoxSizer(wx.VERTICAL)
        url_sizer.Add(wx.StaticText(self, wx.ID_ANY, "URL"), 0, wx.BOTTOM, 4)
        self._txt_base_url = wx.TextCtrl(self, wx.ID_ANY, self.DEFAULT_URL)
        url_sizer.Add(self._txt_base_url, 0, wx.EXPAND)
        self._main_sizer.Add(url_sizer, 0, wx.EXPAND | wx.ALL, 10)

        # Browser label + hint
        lbl_browser: wx.StaticText = wx.StaticText(
            self, wx.ID_ANY, "Select browser")
        lbl_browser.SetFont(wx.Font(10,
                                    wx.FONTFAMILY_DEFAULT,
                                    wx.FONTSTYLE_NORMAL,
                                    wx.FONTWEIGHT_BOLD))
        self._main_sizer.Add(lbl_browser, 0, wx.LEFT | wx.RIGHT, 10)

        hint: wx.StaticText = wx.StaticText(
            self, wx.ID_ANY,
            "The selected browser must be installed on this system.")
        hint.SetForegroundColour(wx.Colour(120, 120, 120))
        self._main_sizer.Add(hint, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)

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
        self._main_sizer.Add(
            scroll,
            0,
            wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM,
            10)

        # Launch browser checkbox
        self._chk_launch_browser: wx.CheckBox = wx.CheckBox(
            self,
            wx.ID_ANY,
            "Launch browser automatically. Uncheck if browser is already running.")
        self._main_sizer.Add(self._chk_launch_browser,
                             0,
                             wx.LEFT | wx.RIGHT | wx.BOTTOM,
                             10)

        # Button bar
        self._create_buttons_bar(self._on_next_click_event)

        self.SetSizerAndFit(self._main_sizer)
        self.CentreOnParent()

    def _on_browser_toggle_event(self, event: wx.CommandEvent) -> None:
        """
            Ensure that only one browser toggle button can be active at a time.

            When a browser button is clicked, this handler deactivates all other
            buttons in ``browser_buttons`` to enforce exclusive selection.
        """
        clicked: wx.Window = event.GetEventObject()

        for _name, btn in self._browser_buttons:
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
        """
        Handle the Next button click event.

        Validates the current page input and, if validation succeeds, closes the
        dialog and signals successful completion so the wizard can proceed to
        the next page.
        """
        if not self._validate_fields():
            return

        self.EndModal(wx.ID_OK)
