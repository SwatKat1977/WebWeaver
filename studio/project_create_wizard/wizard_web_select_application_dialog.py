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
from browser_icons import (bitmap_from_base64,
                           CHROMIUM_BROWSER_ICON,
                           CHROME_BROWSER_ICON,
                           FIREFOX_BROWSER_ICON,
                           MICROSOFT_EDGE_BROWSER_ICON)
from studio.project_create_wizard_step_indicator import ProjectCreateWizardStepIndicator


class WizardWebSelectApplicationDialog(wx.Dialog):
    """
    A wizard step dialog for selecting the target web browser and URL.

    This dialog represents the second step of the project creation wizard,
    allowing the user to choose which web browser to test their application on
    and to specify the initial URL to load. The layout includes:

    * a visual step indicator
    * a header with title and description
    * an editable URL field
    * a scrollable list of browser options (Firefox, Chrome, Chromium, Edge)
    * a checkbox allowing automatic browser launch
    * Back / Continue buttons to control wizard navigation

    The available browsers are displayed using toggleable bitmap buttons, and
    only one browser may be selected at a time. An internal handler ensures
    mutual exclusivity between the browser buttons.

    Parameters
    ----------
    parent : wx.Window
        The parent window or panel that owns this dialog.

    Attributes
    ----------
    url : wx.TextCtrl
        The text box containing the URL used for testing (defaults to
        ``DEFAULT_URL``).
    browser_buttons : list[wx.BitmapToggleButton]
        A list of toggle buttons representing supported browsers.
    chk_launch : wx.CheckBox
        Checkbox determining whether the selected browser should be launched
        automatically.
    DEFAULT_URL : str
        Default value shown in the URL text field.
    SUB_TEXT_FOREGROUND_COLOUR : str
        Colour used for descriptive subtext.
    HINT_FOREGROUND_COLOUR : str
        Colour used for hint text.
    LABEL_FOREGROUND_COLOUR : str
        Colour used for browser labels.
    """

    DEFAULT_URL: str = "https://webweaverautomation.com/"
    SUB_TEXT_FOREGROUND_COLOUR: str = "#777777"
    HINT_FOREGROUND_COLOUR: str = "#777777"
    LABEL_FOREGROUND_COLOUR: str = "#555555"

    def __init__(self, parent):
        super().__init__(
            parent,
            title="Create your new solution | Select web browser",
            style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER
        )

        main = wx.BoxSizer(wx.VERTICAL)

        # --- Step Header ---
        main.Add(ProjectCreateWizardStepIndicator(self, active_index=1),
                 0, wx.EXPAND | wx.ALL, 10)

        # --- Header text ---
        header = wx.BoxSizer(wx.HORIZONTAL)
        icon = wx.ArtProvider.GetBitmap(wx.ART_TIP, wx.ART_OTHER, (48, 48))
        header.Add(wx.StaticBitmap(self, bitmap=icon), 0, wx.ALL, 10)

        text = wx.BoxSizer(wx.VERTICAL)
        title = wx.StaticText(self, label="Set up your web browser")
        title.SetFont(wx.Font(15, wx.DEFAULT, wx.NORMAL, wx.BOLD))
        sub = wx.StaticText(
            self,
            label="Which web browser do you want to test on?"
        )
        sub.SetForegroundColour(self.SUB_TEXT_FOREGROUND_COLOUR)

        text.Add(title)
        text.Add(sub, 0, wx.TOP, 4)
        header.Add(text, 1, wx.ALIGN_CENTER_VERTICAL)

        main.Add(header, 0, wx.LEFT | wx.RIGHT, 10)

        # --- URL area ---
        url_section = wx.BoxSizer(wx.VERTICAL)
        url_section.Add(wx.StaticText(self, label="URL"), 0, wx.BOTTOM, 4)
        self.url = wx.TextCtrl(self, value=self.DEFAULT_URL)
        url_section.Add(self.url, 0, wx.EXPAND)
        main.Add(url_section, 0, wx.EXPAND | wx.ALL, 15)

        # --- Browser label ---
        lbl_browser = wx.StaticText(self, label="Select browser")
        lbl_browser.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD))
        main.Add(lbl_browser, 0, wx.LEFT | wx.RIGHT, 15)

        hint = wx.StaticText(self,
                             label="The selected browser must be installed on this system.")
        hint.SetForegroundColour(self.HINT_FOREGROUND_COLOUR)
        main.Add(hint, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 15)

        # ---------------------------------------------------------------
        #   SCROLLABLE BROWSER LIST (just like Ranorex)
        # ---------------------------------------------------------------
        scroll = wx.ScrolledWindow(self, style=wx.HSCROLL | wx.VSCROLL)
        scroll.SetScrollRate(10, 10)

        browser_sizer = wx.BoxSizer(wx.HORIZONTAL)

        chromium_bmp = bitmap_from_base64(CHROMIUM_BROWSER_ICON)
        chrome_bmp = bitmap_from_base64(CHROME_BROWSER_ICON)
        firefox_bmp = bitmap_from_base64(FIREFOX_BROWSER_ICON)
        ms_edge_bmp = bitmap_from_base64(MICROSOFT_EDGE_BROWSER_ICON)

        # List of browsers
        browsers = [
            ("Firefox", firefox_bmp),
            ("Chrome", chrome_bmp),
            ("Chromium", chromium_bmp),
            ("Edge (Chromium)", ms_edge_bmp),
        ]

        self.browser_buttons = []

        for name, bitmap_entry in browsers:
            column = wx.BoxSizer(wx.VERTICAL)

            btn = wx.BitmapToggleButton(
                scroll,
                -1,
                bitmap_entry
            )

            label = wx.StaticText(scroll, label=name)
            label.SetForegroundColour(self.LABEL_FOREGROUND_COLOUR)

            column.Add(btn, 0, wx.ALIGN_CENTER | wx.BOTTOM, 4)
            column.Add(label, 0, wx.ALIGN_CENTER)

            browser_sizer.Add(column, 0, wx.RIGHT, 25)

            btn.Bind(wx.EVT_TOGGLEBUTTON, self.__on_browser_toggle)
            self.browser_buttons.append(btn)

        scroll.SetSizer(browser_sizer)
        scroll.SetMinSize((-1, 85))  # good height for icon + label
        main.Add(scroll, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 15)

        # --- Checkbox ---
        self.chk_launch = wx.CheckBox(
            self,
            label="Launch browser automatically. Uncheck if browser is already running."
        )
        main.Add(self.chk_launch, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 15)

        # --- Buttons ---
        buttons = wx.BoxSizer(wx.HORIZONTAL)
        buttons.AddStretchSpacer()
        back = wx.Button(self, label="Back")
        cont = wx.Button(self, label="Continue")
        back.Bind(wx.EVT_BUTTON, lambda e: self.EndModal(wx.ID_CANCEL))
        cont.Bind(wx.EVT_BUTTON, lambda e: self.EndModal(wx.ID_OK))

        buttons.Add(back, 0, wx.RIGHT, 10)
        buttons.Add(cont)
        main.Add(buttons, 0, wx.EXPAND | wx.ALL, 15)

        self.SetSizerAndFit(main)
        self.Centre()

    # --- Make selection exclusive ---
    def __on_browser_toggle(self, event):
        """
        Ensure that only one browser toggle button can be active at a time.

        When a browser button is clicked, this handler deactivates all other
        buttons in ``browser_buttons`` to enforce exclusive selection.
        """
        clicked = event.GetEventObject()
        for b in self.browser_buttons:
            if b != clicked:
                b.SetValue(False)
