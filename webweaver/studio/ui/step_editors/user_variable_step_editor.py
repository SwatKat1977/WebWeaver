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
    """Dialog for editing a user variable recording step.

    This dialog allows the user to configure a variable name and value
    associated with a recording step. The existing payload is loaded into
    editable fields and, if validation succeeds, the updated values are
    written back into the event payload.
    """
    # pylint: disable=too-few-public-methods

    def __init__(self, parent, event: dict):
        """Initialize the user variable editor dialog.

        Args:
            parent (wx.Window):
                The parent window that owns the dialog.
            event (dict):
                The recording step event dictionary containing a ``payload``
                entry with the user variable data to edit.
        """
        super().__init__(
            parent,
            "Edit User Variable",
            "Edit User Variable",
            "Configure a user variable.")

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

    def _validate(self):
        """Validate user input and update the event payload.

        Ensures that the variable name field is populated. If validation
        succeeds, a new :class:`UserVariablePayload` is constructed from the
        field values and written back into the event dictionary.

        Returns:
            bool: ``True`` if validation succeeds and the payload was updated,
            otherwise ``False``.
        """
        field_label = self._field_step_label.GetValue().strip()
        field_name = self._field_variable_name.GetValue().strip()
        field_value = self._field_variable_value.GetValue().strip()

        if not field_name:
            wx.MessageBox("User variable name is required",
                          "Validation Error", wx.ICON_ERROR)
            self._field_variable_name.SetFocus()
            return False

        new_payload = UserVariablePayload(
            label=field_label,
            name=field_name,
            value=field_value)

        self._event["payload"] = dataclasses.asdict(new_payload)
        self.changed = True

        return True
