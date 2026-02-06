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
import dataclasses
import wx
from ..persistence.recording_document import DomClickPayload


class ClickStepEditor(wx.Dialog):
    """
    Dialog window for editing a DOM click step event.

    Allows the user to modify the XPath associated with a recorded click event.
    The dialog operates directly on the provided event dictionary and updates
    its payload if the user confirms the changes.

    Attributes:
        changed (bool): Indicates whether the event was modified by the user.
    """
    # pylint: disable=too-few-public-methods

    def __init__(self, parent, index: int, event: dict):
        """
        Initialize the ClickStepEditor dialog.

        Args:
            parent: The parent wxPython window.
            index (int): The index of the step being edited.
            event (dict): The event data dictionary containing a "payload"
                field with click information.
        """
        super().__init__(parent, title="Edit Click Step")

        self.changed = False
        self._index = index
        self._event = event

        payload = DomClickPayload(**event.get("payload", {}))

        self.xpath_ctrl = wx.TextCtrl(self, value=payload.xpath)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(wx.StaticText(self, label="XPath:"), 0, wx.ALL, 5)
        sizer.Add(self.xpath_ctrl, 0, wx.EXPAND | wx.ALL, 5)

        sizer.Add(
            self.CreateButtonSizer(wx.OK | wx.CANCEL),
            0, wx.ALL | wx.ALIGN_RIGHT, 10
        )

        self.SetSizerAndFit(sizer)

        self.Bind(wx.EVT_BUTTON, self._on_ok, id=wx.ID_OK)

    def _on_ok(self, _evt):
        """
        Handle the OK button event.

        Updates the event payload with the modified XPath value,
        marks the dialog as changed, and closes the dialog with
        an OK result.
        """
        new_payload = DomClickPayload(
            xpath=self.xpath_ctrl.GetValue()
        )

        self._event["payload"] = dataclasses.asdict(new_payload)
        self.changed = True

        self.EndModal(wx.ID_OK)
