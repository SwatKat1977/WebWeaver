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
import json
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
                         size=(600, 600))

        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)

        # URL input
        self.url_input = wx.TextCtrl(panel)
        sizer.Add(self.url_input, 0, wx.EXPAND | wx.ALL, 5)

        # Buttons
        open_btn = wx.Button(panel, label="Open Page")
        open_btn.Bind(wx.EVT_BUTTON, self.__on_open)
        sizer.Add(open_btn, 0, wx.ALL, 5)

        # Start inspection mode button
        inspect_btn = wx.Button(panel, label="Start Inspect Mode")
        inspect_btn.Bind(wx.EVT_BUTTON, self.__on_start_inspect)
        sizer.Add(inspect_btn, 0, wx.ALL, 5)

        # Stop inspection mode button
        stop_inspect = wx.Button(panel, label="Stop Inspect Mode")
        stop_inspect.Bind(wx.EVT_BUTTON, self.__on_stop_inspect)
        sizer.Add(stop_inspect, 0, wx.ALL, 5)

        # Start record mode
        record_btn = wx.Button(panel, label="Start Record Mode")
        record_btn.Bind(wx.EVT_BUTTON, self.__on_start_record)
        sizer.Add(record_btn, 0, wx.ALL, 5)

        # Stop record mode
        stop_record_btn = wx.Button(panel, label="Stop Record Mode")
        stop_record_btn.Bind(wx.EVT_BUTTON, self.__on_stop_record)
        sizer.Add(stop_record_btn, 0, wx.ALL, 5)

        save_json_btn = wx.Button(panel, label="Save Recording to JSON")
        save_json_btn.Bind(wx.EVT_BUTTON, self.__on_save_json)
        sizer.Add(save_json_btn, 0, wx.ALL, 5)

        # Output
        self.output = wx.TextCtrl(panel, style=wx.TE_MULTILINE | wx.TE_READONLY)
        sizer.Add(self.output, 1, wx.EXPAND | wx.ALL, 5)

        panel.SetSizer(sizer)

        # Browser controller
        self.browser = BrowserController(self.__on_event_received)
        self.recorded_session = []

    # -------------------------
    # Button handlers
    # -------------------------
    def __on_open(self, _event):
        """Handle the Open Page button press.

        Retrieves the URL from the text input and instructs the browser
        controller to load the page.
        """
        self.browser.open_page(self.url_input.GetValue())

    def __on_start_inspect(self, _event):
        # Reset display + session
        self.output.Clear()  # Clear output text field
        self.recorded_session = []  # Reset stored events

        self.browser.disable_record_mode()
        self.browser.enable_inspect_mode()

        t = threading.Thread(target=self.browser.listen_for_click, daemon=True)
        t.start()

    def __on_stop_inspect(self, _event):
        """Stop inspect mode by telling the browser controller to disable it."""
        self.browser.disable_inspect_mode()

    def __on_start_record(self, _event):
        # Reset display + session
        self.output.Clear()  # Clear output text field
        self.recorded_session = []  # Reset stored events

        # Reset JS recorder buffer
        self.browser.driver.execute_script("window.__recorded_actions = [];")
        self.browser.driver.execute_script("window.__recorded_outgoing = [];")

        self.browser.disable_inspect_mode()
        self.browser.enable_record_mode()

        t = threading.Thread(target=self.browser.listen_for_click, daemon=True)
        t.start()

    def __on_stop_record(self, _event):
        self.browser.disable_record_mode()

    # -------------------------
    # Event callback
    # -------------------------
    def __on_event_received(self, data):
        self.output.AppendText(data + "\n\n")
        self.recorded_session.append(json.loads(data))

    def __on_save_json(self, _event):
        if not self.recorded_session:
            wx.MessageBox("No recorded events to save.", "Info")
            return

        with wx.FileDialog(
            self,
            "Save JSON",
            wildcard="JSON files (*.json)|*.json",
            style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT
        ) as dlg:

            if dlg.ShowModal() == wx.ID_CANCEL:
                return  # User cancelled

            path = dlg.GetPath()
            try:
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(self.recorded_session, f, indent=2)
                wx.MessageBox("Recording saved successfully!", "Saved")

            except (OSError, TypeError) as e:
                wx.MessageBox(f"Error saving file:\n{e}", "Error")
