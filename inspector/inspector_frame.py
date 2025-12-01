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
import threading
from browser_controller import BrowserController


class InspectorFrame(wx.Frame):
    def __init__(self):
        super().__init__(None, title="WebWeaver Inspector (Selenium)",
                         size=(500, 500))

        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)

        # URL input
        self.url_input = wx.TextCtrl(panel)
        sizer.Add(self.url_input, 0, wx.EXPAND | wx.ALL, 5)

        # Open Page button
        open_btn = wx.Button(panel, label="Open Page")
        open_btn.Bind(wx.EVT_BUTTON, self.on_open)
        sizer.Add(open_btn, 0, wx.ALL, 5)

        # Start inspection mode button
        start_btn = wx.Button(panel, label="Start Inspect Mode")
        start_btn.Bind(wx.EVT_BUTTON, self.on_start_inspect)
        sizer.Add(start_btn, 0, wx.ALL, 5)

        # Stop inspection mode button
        stop_btn = wx.Button(panel, label="Stop Inspect Mode")
        stop_btn.Bind(wx.EVT_BUTTON, self.on_stop_inspect)
        sizer.Add(stop_btn, 0, wx.ALL, 5)

        # Output box
        self.output = wx.TextCtrl(panel, style=wx.TE_MULTILINE | wx.TE_READONLY)
        sizer.Add(self.output, 1, wx.EXPAND | wx.ALL, 5)

        panel.SetSizer(sizer)

        # Browser controller
        self.browser = BrowserController(self.on_element_selected)

    def on_open(self, event):
        url = self.url_input.GetValue()
        self.browser.open_page(url)

    def on_start_inspect(self, event):
        """ Start Inspect Mode """
        # Force reinjection of inspector.js BEFORE enabling inspect mode
        self.browser.force_reinject_inspector()

        # Turn on inspect mode
        self.browser.enable_inspect_mode()

        # Start listener fresh every time
        threading.Thread(target=self.browser.listen_for_click, daemon=True).start()

    def on_stop_inspect(self, event):
        """ Stop Inspect Mode """
        self.browser.disable_inspect_mode()

    def on_element_selected(self, data):
        self.output.SetValue(data)
