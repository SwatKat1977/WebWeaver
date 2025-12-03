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
from project_create_wizard.browser_icons import (
    bitmap_from_base64,
    CHROMIUM_BROWSER_ICON,
    CHROME_BROWSER_ICON,
    FIREFOX_BROWSER_ICON,
    MICROSOFT_EDGE_BROWSER_ICON)
from wizard_base_page import WizardBasePage


class WizardWebSelectBrowserPage(WizardBasePage):
    """
    A wizard step page for selecting the target web browser and URL.

    This page represents the second step of the project creation wizard,
    allowing the user to choose which web browser to test their application on
    and to specify the initial URL to load. The layout includes:
    * an editable URL field
    * a scrollable list of browser options (Firefox, Chrome, Chromium, Edge)
    * a checkbox allowing automatic browser launch

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
    DEFAULT_URL: str = "https://www.example.com"
    SUB_TEXT_FOREGROUND_COLOUR: str = "#777777"
    HINT_FOREGROUND_COLOUR: str = "#777777"
    LABEL_FOREGROUND_COLOUR: str = "#555555"

    def __init__(self, parent, wizard):
        super().__init__(
            parent,
            wizard,
            title="Set up your web test",
            subtitle="Which web browser do you want to test on?"
        )

        main = wx.BoxSizer(wx.VERTICAL)

        # URL field
        url_sizer = wx.BoxSizer(wx.VERTICAL)
        url_sizer.Add(wx.StaticText(self, label="URL"), 0, wx.BOTTOM, 4)
        self.url = wx.TextCtrl(self, value=self.DEFAULT_URL)
        url_sizer.Add(self.url, 0, wx.EXPAND)
        main.Add(url_sizer, 0, wx.EXPAND | wx.ALL, 10)

        # Browser selection label
        lbl_browser = wx.StaticText(self, label="Select browser")
        lbl_browser.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        main.Add(lbl_browser, 0, wx.LEFT | wx.RIGHT, 10)

        hint = wx.StaticText(self, label="The selected browser must be installed on this system.")
        hint.SetForegroundColour(wx.Colour(120, 120, 120))
        main.Add(hint, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)

        # Scrollable browser icons (simplified, using ArtProvider)
        scroll = wx.ScrolledWindow(self, style=wx.HSCROLL | wx.BORDER_NONE)
        scroll.SetScrollRate(10, 0)
        scroll.SetMinSize((-1, 90))

        hsizer = wx.BoxSizer(wx.HORIZONTAL)

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
        for name, bmp in browsers:
            col = wx.BoxSizer(wx.VERTICAL)
            btn = wx.BitmapToggleButton(scroll, -1, bmp)
            label = wx.StaticText(scroll, label=name)
            label.SetForegroundColour(wx.Colour(80, 80, 80))

            col.Add(btn, 0, wx.ALIGN_CENTER | wx.BOTTOM, 4)
            col.Add(label, 0, wx.ALIGN_CENTER)
            hsizer.Add(col, 0, wx.RIGHT, 20)

            btn.Bind(wx.EVT_TOGGLEBUTTON, self.on_browser_toggled)
            self.browser_buttons.append((name, btn))

        scroll.SetSizer(hsizer)
        main.Add(scroll, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)

        # Checkbox
        self.chk_launch = wx.CheckBox(
            self,
            label="Launch browser automatically. Uncheck if browser is already running.",
        )
        main.Add(self.chk_launch, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)

        self.SetSizer(main)

    def on_browser_toggled(self, event):
        """
        Ensure that only one browser toggle button can be active at a time.

        When a browser button is clicked, this handler deactivates all other
        buttons in ``browser_buttons`` to enforce exclusive selection.
        """
        clicked = event.GetEventObject()
        for name, btn in self.browser_buttons:
            if btn is not clicked:
                btn.SetValue(False)

    def validate(self) -> bool:
        url = self.url.GetValue().strip()
        if not url:
            wx.MessageBox("Please enter a URL.", "Missing information", wx.ICON_WARNING)
            return False

        selected = None
        for name, btn in self.browser_buttons:
            if btn.GetValue():
                selected = name
                break

        if not selected:
            wx.MessageBox("Please select a browser.", "Missing information", wx.ICON_WARNING)
            return False

        self.wizard.shared_data["url"] = url
        self.wizard.shared_data["browser"] = selected
        self.wizard.shared_data["launch_auto"] = self.chk_launch.GetValue()
        return True