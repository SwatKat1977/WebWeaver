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
from ..persistence.recording_document import NavGotoPayload


class NavGotoStepEditor(wx.Dialog):
    """Dialog for editing a navigation step.

    Allows the user to modify the destination URL associated with a
    NAV_GOTO recording event.

    Attributes:
        changed: Indicates whether the event was modified by the user.
    """
    # pylint: disable=too-few-public-methods

    def __init__(self, parent, _index: int, event: dict):
        """Initialize the NavGotoStepEditor dialog.

        Args:
            parent: The parent wxPython window.
            _index: Index of the step being edited (unused but included
                for interface consistency with other editors).
            event: The event dictionary containing the payload to edit.
        """
        super().__init__(parent, title="Edit Navigate Step")

        self.changed = False
        self._event = event

        payload = NavGotoPayload(**event.get("payload", {}))

        self.url_ctrl = wx.TextCtrl(self, value=payload.url)

        sizer = wx.BoxSizer(wx.VERTICAL)

        sizer.Add(wx.StaticText(self, label="URL:"), 0, wx.ALL, 5)
        sizer.Add(self.url_ctrl, 0, wx.EXPAND | wx.ALL, 5)

        sizer.Add(self.CreateButtonSizer(wx.OK | wx.CANCEL),
                  0, wx.ALL | wx.ALIGN_RIGHT, 10)

        self.SetSizerAndFit(sizer)

        self.Bind(wx.EVT_BUTTON, self._on_ok, id=wx.ID_OK)

    def _on_ok(self, _evt):
        """Handle confirmation of the dialog.

        Updates the event payload with the modified XPath and
        checked state, marks the dialog as changed, and closes
        the dialog with an OK result.
        """
        new_payload = NavGotoPayload(
            url=self.url_ctrl.GetValue()
        )

        self._event["payload"] = dataclasses.asdict(new_payload)
        self.changed = True
        self.EndModal(wx.ID_OK)
