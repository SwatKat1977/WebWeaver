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
from webweaver.studio.persistence.recording_document import WaitPayload
from webweaver.studio.ui.fancy_dialog_base import FancyDialogBase


class WaitStepEditor(FancyDialogBase):
    """Dialog for editing a wait step.

    Allows the user to modify the duration of a WAIT recording event.

    Attributes:
        changed: Indicates whether the event was modified by the user.
    """
    # pylint: disable=too-few-public-methods

    def __init__(self, parent, event: dict):
        """Initialize the WaitStepEditor dialog.

        Args:
            parent: The parent wxPython window.
            event: The event dictionary containing the payload to edit.
        """
        super().__init__(
            parent,
            "Edit Wait Step",
            "Edit Wait Step",
            "Configure how automation performs a wait.")

        self.changed = False
        self._event = event

        payload = WaitPayload(**event.get("payload", {}))

        # Step Label
        self._field_step_label = self.add_field("Step Label:", wx.TextCtrl)
        self._field_step_label.SetValue(payload.label)

        # Duration (ms)
        self._field_duration: wx.SpinCtrl = self.add_field("Duration (ms):",
                                                           wx.SpinCtrl)
        self._field_duration.SetMin(0)
        self._field_duration.SetMax(600000)
        self._field_duration.SetValue(payload.duration_ms)

        self.finalise()

    def _ok_event(self):
        new_payload = WaitPayload(
            label=self._field_step_label.GetValue().strip(),
            duration_ms=self._field_duration.GetValue())

        self._event["payload"] = dataclasses.asdict(new_payload)
        self.changed = True
        self.EndModal(wx.ID_OK)
