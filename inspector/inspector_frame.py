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
import threading
import wx
from browser_controller import BrowserController


class InspectorFrame(wx.Frame):
    """Main wxPython UI frame for the WebWeaver Inspector tool.

    This frame provides:
    - A text box for entering a URL
    - Buttons for opening the page, starting inspect mode, and stopping inspect mode
    - A multiline read-only output area showing the clicked element data from Selenium
    - Integration with the BrowserController, which handles Selenium operations

    The frame communicates with Selenium through callbacks and updates the GUI
    in response to element selection events coming from the browser.
    """
    # pylint: disable=too-few-public-methods

    def __init__(self):
        """Initialize the inspector frame and build the wxPython UI."""
        super().__init__(None, title="WebWeaver Inspector (Selenium)",
                         size=(500, 500))

        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)

        # URL input
        self.url_input = wx.TextCtrl(panel)
        sizer.Add(self.url_input, 0, wx.EXPAND | wx.ALL, 5)

        # Open Page button
        open_btn = wx.Button(panel, label="Open Page")
        open_btn.Bind(wx.EVT_BUTTON, self.__on_open)
        sizer.Add(open_btn, 0, wx.ALL, 5)

        # Start inspection mode button
        start_btn = wx.Button(panel, label="Start Inspect Mode")
        start_btn.Bind(wx.EVT_BUTTON, self.__on_start_inspect)
        sizer.Add(start_btn, 0, wx.ALL, 5)

        # Stop inspection mode button
        stop_btn = wx.Button(panel, label="Stop Inspect Mode")
        stop_btn.Bind(wx.EVT_BUTTON, self.__on_stop_inspect)
        sizer.Add(stop_btn, 0, wx.ALL, 5)

        # Output box
        self.output = wx.TextCtrl(panel,
                                  style=wx.TE_MULTILINE | wx.TE_READONLY)
        sizer.Add(self.output, 1, wx.EXPAND | wx.ALL, 5)

        panel.SetSizer(sizer)

        # Browser controller
        self.browser = BrowserController(self.on_element_selected)

    def __on_open(self, _event):
        """Handle the Open Page button press.

        Retrieves the URL from the text input and instructs the browser
        controller to load the page.
        """
        url = self.url_input.GetValue()
        self.browser.open_page(url)

    def __on_start_inspect(self, _event):
        self.browser.driver.execute_script("window.__FORCE_INSPECT_MODE = true;")
        self.browser.enable_inspect_mode()

        # Debug print - tell us if JS is working
        print("INSPECT MODE FLAG =", self.browser.driver.execute_script(
            "return window.__INSPECT_MODE;"
        ))

        thread = threading.Thread(
            target=self.browser.listen_for_click,
            daemon=True
        )
        thread.start()

    def __on_stop_inspect(self, _event):
        """Stop inspect mode by telling the browser controller to disable it."""
        self.browser.driver.execute_script("window.__FORCE_INSPECT_MODE = false;")
        self.browser.disable_inspect_mode()

    def on_element_selected(self, data):
        """Callback invoked by BrowserController when an element is selected.

        Parameters
        ----------
        data : str
            JSON-formatted string describing the clicked element.
        """
        self.output.SetValue(data)
