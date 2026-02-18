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


class ScrollStepEditor(wx.Dialog):
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

    def __init__(self, parent, _index: int, event: dict):
        """
        Initialize the scroll step editor dialog.

        Args:
            parent:
                Parent wx widget.
            _index (int):
                Step index in the recording timeline. Currently unused
                but retained for consistency with other step editors.
            event (dict):
                The event dictionary containing an optional ``payload``
                describing the existing scroll configuration.
        """
        super().__init__(parent, title="Edit Scroll Step")

        self.changed = False
        self._event = event

        payload = ScrollPayload(**event.get("payload", {}))

        # Scroll Method Control
        self._method_choice_ctrl = wx.Choice(
            self,
            choices=[label for label, _ in SCROLL_EVENT_TYPE_LABELS])

        # --- Scroll Method ---
        try:
            current_type = ScrollType(payload.scroll_type)
        except ValueError:
            current_type = ScrollType.BOTTOM

        for i, (_, enum_val) in enumerate(SCROLL_EVENT_TYPE_LABELS):
            if enum_val == current_type:
                self._method_choice_ctrl.SetSelection(i)
                break
        else:
            self._method_choice_ctrl.SetSelection(0)

        # --- Location controls ---
        self._x_ctrl = wx.TextCtrl(self, value=str(payload.x_scroll or ""))
        self._y_ctrl = wx.TextCtrl(self, value=str(payload.y_scroll or ""))

        # ======================
        # Layout
        # ======================
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        form = wx.FlexGridSizer(cols=2, hgap=2, vgap=10)
        form.AddGrowableCol(1, 1)

        # Scroll method row
        form.Add(wx.StaticText(self, label="Scroll Method:"),
                 0, wx.ALIGN_CENTER_VERTICAL)
        form.Add(self._method_choice_ctrl, 1, wx.EXPAND)

        # Location row (custom horizontal layout)
        form.Add(wx.StaticText(self, label="Location (X / Y):"),
                 0, wx.ALIGN_CENTER_VERTICAL)
        xy_sizer = wx.BoxSizer(wx.HORIZONTAL)
        xy_sizer.Add(self._x_ctrl, 1, wx.RIGHT, 5)
        xy_sizer.Add(self._y_ctrl, 1)
        form.Add(xy_sizer, 1, wx.EXPAND)
        main_sizer.Add(form, 0, wx.EXPAND | wx.ALL, 10)

        main_sizer.Add(self.CreateButtonSizer(wx.OK | wx.CANCEL),
                       0, wx.ALL | wx.ALIGN_RIGHT, 10)

        self.SetSizer(main_sizer)
        main_sizer.Fit(self)
        self.CentreOnParent()

        self.Bind(wx.EVT_BUTTON, self._on_ok, id=wx.ID_OK)
        self._method_choice_ctrl.Bind(wx.EVT_CHOICE, self._on_method_changed)

        self._update_location_enabled()

    def _on_ok(self, _evt):
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
            self._method_choice_ctrl.GetSelection()
        ]

        x_val = None
        y_val = None

        # Only required for CUSTOM scroll
        if enum_val == ScrollType.CUSTOM:
            try:
                x_val = int(self._x_ctrl.GetValue().strip())
                y_val = int(self._y_ctrl.GetValue().strip())
            except ValueError:
                wx.MessageBox(
                    "X and Y are required for custom scrolling.",
                    "Validation Error",
                    wx.OK | wx.ICON_WARNING
                )
                return

        self._event["payload"] = {
            "scroll_type": enum_val.value,
            "x_scroll": x_val,
            "y_scroll": y_val }

        self.changed = True
        self.EndModal(wx.ID_OK)

    def _update_location_enabled(self):
        """
        Enable or disable coordinate input fields based on scroll type.

        X and Y input controls are only enabled when the selected
        scroll method is ``CUSTOM``.
        """
        selected_index = self._method_choice_ctrl.GetSelection()

        if selected_index == wx.NOT_FOUND:
            self._x_ctrl.Enable(False)
            self._y_ctrl.Enable(False)
            return

        _, method = SCROLL_EVENT_TYPE_LABELS[selected_index]

        self._x_ctrl.Enable(method == ScrollType.CUSTOM)
        self._y_ctrl.Enable(method == ScrollType.CUSTOM)

    def _on_method_changed(self, _evt):
        """
        Handle scroll method selection changes.

        Updates UI control state so only relevant fields are editable.
        """
        self._update_location_enabled()
