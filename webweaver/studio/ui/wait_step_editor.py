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
from persistence.recording_document import WaitPayload


class WaitStepEditor(wx.Dialog):
    """Dialog for editing a wait step.

    Allows the user to modify the duration of a WAIT recording event.

    Attributes:
        changed: Indicates whether the event was modified by the user.
    """
    # pylint: disable=too-few-public-methods

    def __init__(self, parent, _index: int, event: dict):
        """Initialize the WaitStepEditor dialog.

        Args:
            parent: The parent wxPython window.
            _index: Index of the step being edited (unused but included
                for interface consistency with other editors).
            event: The event dictionary containing the payload to edit.
        """
        super().__init__(parent, title="Edit Wait Step")

        self.changed = False
        self._event = event

        payload = WaitPayload(**event.get("payload", {}))

        self.duration_ctrl = wx.SpinCtrl(
            self,
            min=0,
            max=600000,
            initial=payload.duration_ms,
        )

        sizer = wx.BoxSizer(wx.VERTICAL)

        sizer.Add(wx.StaticText(self, label="Duration (ms):"), 0, wx.ALL, 5)
        sizer.Add(self.duration_ctrl, 0, wx.ALL, 5)

        sizer.Add(self.CreateButtonSizer(wx.OK | wx.CANCEL),
                  0, wx.ALL | wx.ALIGN_RIGHT, 10)

        self.SetSizerAndFit(sizer)

        self.Bind(wx.EVT_BUTTON, self._on_ok, id=wx.ID_OK)

    def _on_ok(self, _evt):
        """Handle confirmation of the dialog.

        Updates the event payload with the new duration value,
        marks the dialog as changed, and closes the dialog
        with an OK result.
        """
        new_payload = WaitPayload(
            duration_ms=self.duration_ctrl.GetValue()
        )

        self._event["payload"] = dataclasses.asdict(new_payload)
        self.changed = True
        self.EndModal(wx.ID_OK)
