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
from webweaver.studio.persistence.recording_document import UserVariablePayload
from webweaver.studio.ui.fancy_dialog_base import FancyDialogBase


class UserVariableStepEditor(FancyDialogBase):
    """Dialog for editing a DOM typing step.

    Allows the user to modify the XPath target and the text value
    associated with a DOM_TYPE recording event.

    Attributes:
        changed: Indicates whether the event was modified by the user.
    """
    # pylint: disable=too-few-public-methods

    def __init__(self, parent, event: dict):
        """Initialize the DomTypeEditor dialog.

        Args:
            parent: The parent wxPython window.
            event: The event dictionary containing the payload to edit.
        """
        super().__init__(
            parent,
            "Edit Type Step",
            "Edit Type Step",
            "Configure how automation performs a DOM type.")

        self.changed = False
        self._event = event

        payload = UserVariablePayload(**event.get("payload", {}))

        self._field_step_label = self.add_field("Step Label:", wx.TextCtrl)
        self._field_step_label.SetValue(payload.label)
        self._field_variable_name = self.add_field("Name:", wx.TextCtrl)
        self._field_variable_name.SetValue(payload.name)
        self._field_variable_value = self.add_field("Value:", wx.TextCtrl)
        self._field_variable_value.SetValue(payload.value)

        self.finalise()
