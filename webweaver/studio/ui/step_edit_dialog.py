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
import copy
import wx


class StepEditDialog(wx.Dialog):
    def __init__(self, parent, step: dict):
        super().__init__(parent, title="Edit Step", size=(600, 300))

        self._step = step
        self._payload = step.get("payload", {})
        self._original = copy.deepcopy(step)

        main_sizer = wx.BoxSizer(wx.VERTICAL)

        grid = wx.FlexGridSizer(rows=0, cols=2, vgap=8, hgap=8)
        grid.AddGrowableCol(1, 1)  # Make the field column stretch

        # Action (read-only)
        grid.Add(wx.StaticText(self, label="Action:"), 0, wx.ALIGN_CENTER_VERTICAL)
        grid.Add(wx.StaticText(self, label=step.get("type")), 1, wx.EXPAND)

        # Target
        grid.Add(wx.StaticText(self, label="Target (XPath):"), 0, wx.ALIGN_CENTER_VERTICAL)
        self._target_ctrl = wx.TextCtrl(
            self, value=str(self._payload.get("xpath", "")))
        grid.Add(self._target_ctrl, 1, wx.EXPAND)

        # Value (if any)
        grid.Add(wx.StaticText(self, label="Value:"), 0, wx.ALIGN_CENTER_VERTICAL)
        value = (
            self._payload.get("value")
            or self._payload.get("text")
            or "")
        self._value_ctrl = wx.TextCtrl(self, value=str(value))
        grid.Add(self._value_ctrl, 1, wx.EXPAND)

        main_sizer.Add(grid, 1, wx.EXPAND | wx.ALL, 10)

        # Buttons
        btns = self.CreateSeparatedButtonSizer(wx.OK | wx.CANCEL)
        main_sizer.Add(btns, 0, wx.EXPAND | wx.ALL, 10)

        self.SetSizerAndFit(main_sizer)

    @property
    def changed(self):
        return self._step != self._original

    def TransferDataFromWindow(self):
        self._payload["xpath"] = self._target_ctrl.GetValue()
        if "value" in self._payload:
            self._payload["value"] = self._value_ctrl.GetValue()
        elif "text" in self._payload:
            self._payload["text"] = self._value_ctrl.GetValue()
        return True
