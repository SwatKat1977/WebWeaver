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
from webweaver.studio.persistence.recording_document import NavGotoPayload
from webweaver.studio.ui.fancy_dialog_base import FancyDialogBase


class NavGotoStepEditor(FancyDialogBase):
    """Dialog for editing a navigation step.

    Allows the user to modify the destination URL associated with a
    NAV_GOTO recording event.

    Attributes:
        changed: Indicates whether the event was modified by the user.
    """
    # __pylint disable=too-few-public-methods

    def __init__(self, parent, event: dict):
        """Initialize the NavGotoStepEditor dialog.

        Args:
            parent: The parent wxPython window.
            event: The event dictionary containing the payload to edit.
        """
        super().__init__(parent,
                         "Edit Navigation Step",
                         "Edit Navigation Step",
                         "Configure how the automation navigates.")

        self.changed = False
        self._event = event

        payload = NavGotoPayload(**event.get("payload", {}))

        # Step Label
        self._field_step_label = self.add_field("Step Label:", wx.TextCtrl)
        self._field_step_label.SetValue(payload.label)

        # URL
        self._field_url = self.add_field("URL:", wx.TextCtrl)
        self._field_url.SetValue(payload.url)

        self.finalise()

    def _ok_event(self):
        """Handle confirmation of the dialog.

        Updates the event payload with the modified XPath and
        checked state, marks the dialog as changed, and closes
        the dialog with an OK result.
        """
        new_payload = NavGotoPayload(
            label=self._field_step_label.GetValue().strip(),
            url=self._field_url.GetValue().strip())

        self._event["payload"] = dataclasses.asdict(new_payload)
        self.changed = True
