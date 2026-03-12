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
from webweaver.studio.persistence.recording_document import DomClickPayload
from webweaver.studio.ui.fancy_dialog_base import FancyDialogBase


class ClickStepEditor(FancyDialogBase):
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
        super().__init__(
            parent,
            "Edit Click Step",
            "Edit Click Step",
            "Configure how the automation performs a DOM click.")

        self.changed = False
        self._index = index
        self._event = event

        payload = DomClickPayload(**event.get("payload", {}))

        self._field_step_label = self.add_field("Step Label:", wx.TextCtrl)
        self._field_step_label.SetValue(payload.label)
        self._field_xpath = self.add_field("XPath:", wx.TextCtrl)
        self._field_xpath.SetValue(payload.xpath)

        self.finalise()

    def _ok_event(self):
        """
        Handle the OK button event.

        Updates the event payload with the modified XPath value,
        marks the dialog as changed, and closes the dialog with
        an OK result.
        """
        new_payload = DomClickPayload(
            label=self._field_step_label.GetValue(),
            xpath=self._field_xpath.GetValue())

        self._event["payload"] = dataclasses.asdict(new_payload)
        self.changed = True
