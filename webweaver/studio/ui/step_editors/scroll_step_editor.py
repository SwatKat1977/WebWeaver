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
from enum import Enum
import wx
from webweaver.studio.persistence.recording_document import ScrollPayload
from webweaver.studio.ui.fancy_dialog_base import FancyDialogBase


class ScrollType(Enum):
    """
    Supported scroll behaviours for a recorded scroll step.

    Values are persisted as lowercase strings within the recording
    payload and determine how playback performs scrolling:

    - TOP: Scroll to the top of the document.
    - BOTTOM: Scroll to the bottom of the document.
    - CUSTOM: Scroll to a specific X/Y coordinate.
    """

    BOTTOM = "bottom"
    CUSTOM = "custom"
    TOP = "top"


SCROLL_EVENT_TYPE_LABELS: list[tuple[str, ScrollType]] = [
    ("Bottom", ScrollType.BOTTOM),
    ("Custom", ScrollType.CUSTOM),
    ("Top", ScrollType.TOP)
]


class ScrollStepEditor(FancyDialogBase):
    """
    Dialog for creating or editing a scroll playback step.

    The editor allows the user to select a scroll strategy
    (top, bottom, or custom coordinates). For custom scrolling,
    X and Y coordinates are required.

    The provided ``event`` dictionary is edited in place. If the
    user confirms the dialog, the updated payload is written back
    to ``event["payload"]``.

    Attributes:
        changed (bool):
            True when the dialog is accepted with valid changes.
        _event (dict):
            The step event being modified.
    """
    # pylint: disable=too-few-public-methods

    def __init__(self, parent, index: int, event: dict):
        """
        Initialize the scroll step editor dialog.

        Args:
            parent:
                Parent wx widget.
            index (int):
                Step index in the recording timeline. Currently unused
                but retained for consistency with other step editors.
            event (dict):
                The event dictionary containing an optional ``payload``
                describing the existing scroll configuration.
        """
        super().__init__(
            parent,
            "Edit Scroll Step",
            "Edit Scroll Step",
            "Configure how the automation performs a Scroll.")

        self.changed = False
        self._index = index
        self._event = event

        payload = ScrollPayload(**event.get("payload", {}))

        # -- Step Label
        self._field_step_label = self.add_field("Step Label:", wx.TextCtrl)
        self._field_step_label.SetValue(payload.label)

        # -- Scroll Method
        self._field_scroll_method = self.add_field(
            "Scroll Method:",
            lambda parent: wx.Choice(
                parent,
                choices=[label for label, _ in SCROLL_EVENT_TYPE_LABELS]))

        # --- Scroll Method ---
        try:
            current_type = ScrollType(payload.scroll_type)
        except ValueError:
            current_type = ScrollType.BOTTOM

        for i, (_, enum_val) in enumerate(SCROLL_EVENT_TYPE_LABELS):
            if enum_val == current_type:
                self._field_scroll_method.SetSelection(i)
                break
        else:
            self._field_scroll_method.SetSelection(0)

        x_y_fields = self.add_two_connected_fields("Location:",
                                                   wx.TextCtrl,
                                                   "[X]",
                                                   wx.TextCtrl,
                                                   "[Y]")
        self._field_x = x_y_fields[0]
        x_value = str(payload.x_scroll) if payload.x_scroll else ""
        y_value = str(payload.y_scroll) if payload.y_scroll else ""
        self._field_x.SetValue(x_value)
        self._field_y = x_y_fields[1]
        self._field_y.SetValue(str(y_value))

        self.finalise()

        self._field_scroll_method.Bind(wx.EVT_CHOICE, self._on_method_changed)

        self._update_location_enabled()

    def _validate(self):
        """
        Validate inputs and persist dialog values into the event payload.

        For CUSTOM scrolling, both X and Y coordinates must be valid
        integers. For TOP and BOTTOM modes, coordinate values are ignored
        and stored as ``None``.

        On successful validation:
            - Updates ``self._event["payload"]``.
            - Sets ``self.changed`` to True.
            - Closes the dialog with ``wx.ID_OK``.
        """
        _, enum_val = SCROLL_EVENT_TYPE_LABELS[
            self._field_scroll_method.GetSelection()]

        x_val = None
        y_val = None

        # Only required for CUSTOM scroll
        if enum_val == ScrollType.CUSTOM:
            try:
                x_val = int(self._field_x.GetValue().strip())
                y_val = int(self._field_y.GetValue().strip())

            except ValueError:
                wx.MessageBox(
                    "X and Y are required for custom scrolling.",
                    "Validation Error",
                    wx.OK | wx.ICON_WARNING
                )
                return False

        self._event["payload"] = {
            "label": self._field_step_label.GetValue().strip(),
            "scroll_type": enum_val.value,
            "x_scroll": x_val,
            "y_scroll": y_val }

        self.changed = True
        return True

    def _update_location_enabled(self):
        """
        Enable or disable coordinate input fields based on scroll type.

        X and Y input controls are only enabled when the selected
        scroll method is ``CUSTOM``.
        """
        selected_index = self._field_scroll_method.GetSelection()

        if selected_index == wx.NOT_FOUND:
            self._field_x.Enable(False)
            self._field_y.Enable(False)
            return

        _, method = SCROLL_EVENT_TYPE_LABELS[selected_index]

        self._field_x.Enable(method == ScrollType.CUSTOM)
        self._field_y.Enable(method == ScrollType.CUSTOM)

    def _on_method_changed(self, _evt):
        """
        Handle scroll method selection changes.

        Updates UI control state so only relevant fields are editable.
        """
        self._update_location_enabled()
