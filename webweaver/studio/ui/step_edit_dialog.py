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
    """
    Modal dialog for editing a single recorded step.

    This dialog provides a simple form-based editor for a recording step
    dictionary as stored in a `.wwrec` recording file. It currently supports
    editing:

        - The target XPath
        - An optional value/text payload (for type/select actions, etc.)

    The action/type itself is shown as read-only and cannot be changed.

    The dialog edits the provided `step` dictionary *in place* if the user
    accepts the dialog. A deep copy of the original step is kept so callers
    can detect whether any changes were made.

    Expected step structure (simplified):

        {
            "type": "dom.type" | "dom.click" | ...,
            "payload": {
                "xpath": "...",
                "value": "..." | "text": "..."   # optional
            }
        }
    """

    def __init__(self, parent, step: dict):
        """
        Create a new StepEditDialog.

        :param parent: Parent wx window.
        :param step: The step dictionary to edit. This object may be modified
                     in-place if the user clicks OK.
        """
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
        """
        Return True if the step has been modified by the user.

        This compares the current step dictionary against the deep-copied
        original state captured when the dialog was created.
        """
        return self._step != self._original

    def TransferDataFromWindow(self):
        """
        Transfer values from the dialog controls back into the step dictionary.

        This method updates the step's payload in-place and is called by wx
        when the user accepts the dialog.

        :return: True to indicate successful data transfer.
        """
        # pylint: disable=invalid-name
        self._payload["xpath"] = self._target_ctrl.GetValue()
        if "value" in self._payload:
            self._payload["value"] = self._value_ctrl.GetValue()
        elif "text" in self._payload:
            self._payload["text"] = self._value_ctrl.GetValue()
        return True
