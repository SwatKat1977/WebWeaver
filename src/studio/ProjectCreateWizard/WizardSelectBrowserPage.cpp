/*
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
*/
#ifdef __PORTED_CODE__
import wx
from project_create_wizard.browser_icons import (
    CHROMIUM_BROWSER_ICON,
    CHROME_BROWSER_ICON,
    FIREFOX_BROWSER_ICON,
    MICROSOFT_EDGE_BROWSER_ICON)
from bitmap_utils import BitmapUtils
from wizard_step_indicator import WizardStepIndicator
from project_create_wizard.wizard_ids import ID_BACK_BUTTON

wxmsw33u_core.lib
wxmsw33u_core.lib

class WizardWebSelectBrowserPage(wx.Dialog):
    DEFAULT_URL = "https://www.example.com"

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
        title = wx.StaticText(self, label="Set up your web test")
        title.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT,
                              wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        subtitle = wx.StaticText(
            self, label="Which web browser do you want to test on?")
        subtitle.SetForegroundColour(wx.Colour(100, 100, 100))
        text_box.Add(title, 0)
        text_box.Add(subtitle, 0, wx.TOP, 4)

        header.Add(text_box, 1, wx.ALIGN_CENTER_VERTICAL)
        main.Add(header, 0, wx.LEFT | wx.RIGHT, 10)

        # URL
        url_box = wx.BoxSizer(wx.VERTICAL)
        url_box.Add(wx.StaticText(self, label="URL"), 0, wx.BOTTOM, 4)
        self.txt_url = wx.TextCtrl(self, value=self.DEFAULT_URL)
        url_box.Add(self.txt_url, 0, wx.EXPAND)
        main.Add(url_box, 0, wx.EXPAND | wx.ALL, 10)

        # Browser label + hint
        lbl_browser = wx.StaticText(self, label="Select browser")
        lbl_browser.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT,
                                    wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        main.Add(lbl_browser, 0, wx.LEFT | wx.RIGHT, 10)

        hint = wx.StaticText(
            self, label="The selected browser must be installed on this system.")
        hint.SetForegroundColour(wx.Colour(120, 120, 120))
        main.Add(hint, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)

        # Scrollable browser icons (simplified)
        scroll = wx.ScrolledWindow(self, style=wx.HSCROLL | wx.BORDER_NONE)
        scroll.SetScrollRate(10, 0)
        scroll.SetMinSize((-1, 110))

        hsizer = wx.BoxSizer(wx.HORIZONTAL)

        chromium_bmp = BitmapUtils.bitmap_from_base64(CHROMIUM_BROWSER_ICON)
        chrome_bmp = BitmapUtils.bitmap_from_base64(CHROME_BROWSER_ICON)
        firefox_bmp = BitmapUtils.bitmap_from_base64(FIREFOX_BROWSER_ICON)
        ms_edge_bmp = BitmapUtils.bitmap_from_base64(MICROSOFT_EDGE_BROWSER_ICON)

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

            btn.Bind(wx.EVT_TOGGLEBUTTON, self.on_browser_toggle)
            self.browser_buttons.append((name, btn))

        scroll.SetSizer(hsizer)
        main.Add(scroll, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)

        # Checkbox
        self.chk_launch = wx.CheckBox(
            self,
            label="Launch browser automatically. Uncheck if browser is already running.",
        )
        main.Add(self.chk_launch, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)

        # Button bar
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        btn_sizer.AddStretchSpacer()

        self.btn_cancel = wx.Button(self, wx.ID_CANCEL, "Cancel")
        self.btn_cancel.Bind(wx.EVT_BUTTON, lambda e: self.EndModal(wx.ID_CANCEL))
        btn_sizer.Add(self.btn_cancel, 0, wx.RIGHT, 10)

        btn_back = wx.Button(self, ID_BACK_BUTTON, "Back")
        btn_back.Bind(wx.EVT_BUTTON, lambda e: self.EndModal(ID_BACK_BUTTON))
        btn_sizer.Add(btn_back, 0, wx.RIGHT, 10)

        self.btn_next = wx.Button(self, wx.ID_OK, "Next")
        self.btn_next.Bind(wx.EVT_BUTTON, self.__on_next)
        btn_sizer.Add(self.btn_next, 0)

        main.Add(btn_sizer, 0, wx.EXPAND | wx.ALL, 10)

        self.SetSizerAndFit(main)
        self.CentreOnParent()

    def on_browser_toggle(self, event):
        """
        Ensure that only one browser toggle button can be active at a time.

        When a browser button is clicked, this handler deactivates all other
        buttons in ``browser_buttons`` to enforce exclusive selection.
        """
        clicked = event.GetEventObject()
        for _name, btn in self.browser_buttons:
            if btn is not clicked:
                btn.SetValue(False)

    def __validate(self) -> bool:
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
        url = self.txt_url.GetValue().strip()
        if not url:
            wx.MessageBox("Please enter a URL.", "Missing information", wx.ICON_WARNING)
            return False

        selected_browser = None
        for name, btn in self.browser_buttons:
            if btn.GetValue():
                selected_browser = name
                break

        if not selected_browser:
            wx.MessageBox("Please select a browser.", "Missing information", wx.ICON_WARNING)
            return False

        self.data["base_url"] = self.txt_url.GetValue().strip()
        self.data["browser"] = selected_browser
        self.data["launch_browser_automatically"] = self.chk_launch.GetValue()

        return True

    def __on_next(self, _event):
        if not self.__validate():
            return

        self.EndModal(wx.ID_OK)

#endif  // #ifdef __PORTED_CODE__
