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
from webweaver.studio.persistence.recording_document import DomCheckPayload
from webweaver.studio.ui.fancy_dialog_base import FancyDialogBase


class CheckStepEditor(FancyDialogBase):
    """Dialog for editing a DOM check step.

    Allows the user to modify the XPath target and the checked state
    associated with a DOM_CHECK recording event.

    Attributes:
        changed: Indicates whether the event was modified by the user.
    """
    # _____pylint: disables=too-few-public-methods

    def __init__(self, parent, event: dict):
        """Initialize the CheckStepEditor dialog.

        Args:
            parent: The parent wxPython window.
            event: The event dictionary containing the payload to edit.
        """
        super().__init__(
            parent,
            "Edit Check Step",
            "Edit Check Step",
            "Configure how the automation performs a DOM checkb.")

        self.changed = False
        self._event = event

        payload = DomCheckPayload(**event.get("payload", {}))

        self._field_step_label = self.add_field("Step Label:", wx.TextCtrl)
        self._field_step_label.SetValue(payload.label)
        self._field_xpath = self.add_field("XPath:", wx.TextCtrl)
        self._field_xpath.SetValue(payload.xpath)
        self._field_is_checked = self.add_field("Checked:", wx.CheckBox)
        self._field_is_checked.SetValue(bool(payload.value))

        self.finalise()

    def _ok_event(self):
        """Handle confirmation of the dialog.

        Updates the event payload with the modified XPath and
        checked state, marks the dialog as changed, and closes
        the dialog with an OK result.
        """
        new_payload = DomCheckPayload(
            label=self._field_step_label.GetValue(),
            xpath=self._field_xpath.GetValue(),
            value=self._field_is_checked.GetValue(),
        )

        self._event["payload"] = dataclasses.asdict(new_payload)
        self.changed = True
