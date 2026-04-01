"""
This source file is part of Web Weaver
For the latest info, see https://github.com/SwatKat1977/WebWeaver

Copyright 2025-2026 SwatKat1977

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.
"""
import wx
from webweaver.studio.ui.framework.settings_page import SettingsPage, ValidationResult


class GeneralSettingsPage(SettingsPage):

    def __init__(self, parent, context):
        super().__init__(parent)
        self._context = context

        outer = wx.BoxSizer(wx.VERTICAL)

        # ---- Content container with consistent margins ----
        content = wx.BoxSizer(wx.VERTICAL)

        # ===== Section Title =====
        title = wx.StaticText(self, label="General")
        font = title.GetFont()
        font = font.Bold()
        font.SetPointSize(font.GetPointSize() + 1)
        title.SetFont(font)
        content.Add(title, 0, wx.BOTTOM, 10)

        # ===== Divider line =====
        content.Add(wx.StaticLine(self), 0, wx.EXPAND | wx.BOTTOM, 20)

        # --- Solution Name ---
        label = wx.StaticText(self,
                              label="Solution Name")
        font = label.GetFont()
        font = font.Bold()
        label.SetFont(font)
        content.Add(label, 0, wx.BOTTOM, 6)

        self._solution_name = wx.TextCtrl(self)
        content.Add(self._solution_name, 0, wx.EXPAND | wx.BOTTOM, 12)

        # --- Base URL ---
        label = wx.StaticText(self,
                              label="Base URL")
        font = label.GetFont()
        font = font.Bold()
        label.SetFont(font)
        content.Add(label, 0, wx.BOTTOM, 6)

        self._base_url = wx.TextCtrl(self)
        content.Add(self._base_url, 0, wx.EXPAND | wx.BOTTOM, 12)

        # ---- Launch browser automatically section ----
        self._browser_automatic_checkbox = wx.CheckBox(
            self,
            label="Launch Browser Automatically")
        content.Add(self._browser_automatic_checkbox, 0, wx.BOTTOM, 10)

        # Add content with clean outer padding
        outer.Add(content, 0, wx.ALL | wx.EXPAND, 20)

        # Push everything upward
        outer.AddStretchSpacer()

        self.SetSizer(outer)

    def load(self):
        pass

    def validate(self) -> ValidationResult:
        pass

    def apply(self):
        pass
