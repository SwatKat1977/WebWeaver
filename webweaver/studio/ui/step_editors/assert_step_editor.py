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
import json
import wx
from webweaver.common.assertion_operator import AssertionOperator
from webweaver.studio.persistence.recording_document import AssertPayload
from webweaver.studio.ui.fancy_dialog_base import FancyDialogBase


ASSERTION_OPERATOR_LABELS: list[tuple[str, AssertionOperator]] = [
    ("Equals (==)", AssertionOperator.EQUALS),
    ("Not Equals (!=)", AssertionOperator.NOT_EQUALS),
    ("Greater Than (>)", AssertionOperator.GREATER_THAN),
    ("Less Than (<)", AssertionOperator.LESS_THAN),
    ("Contains", AssertionOperator.CONTAINS),
    ("In", AssertionOperator.IN),
    ("Starts With", AssertionOperator.STARTS_WITH),
    ("Ends With", AssertionOperator.ENDS_WITH),
    ("Matches Regex", AssertionOperator.MATCHES_REGEX),
    ("Is True", AssertionOperator.IS_TRUE),
    ("Is False", AssertionOperator.IS_FALSE),
    ("Is None", AssertionOperator.IS_NONE),
    ("Is Not None", AssertionOperator.IS_NOT_NONE),
]

"""
Set of assertion operators that do not require a right-hand value.

Operators included here are treated as unary during both UI editing
and playback execution. When selected in the editor, the right-hand
input control is disabled and cleared automatically.

This set must remain consistent with the unary operators defined in
`AssertionOperator` to prevent mismatches between UI behavior and
execution logic.
"""
UNARY_ASSERTION_OPERATORS = {
    AssertionOperator.IS_TRUE,
    AssertionOperator.IS_FALSE,
    AssertionOperator.IS_NONE,
    AssertionOperator.IS_NOT_NONE,
}


class AssertionStepEditor(FancyDialogBase):
    """
    Modal dialog for editing an assertion step's payload.

    This dialog allows the user to configure an assertion consisting of:
        - A left-hand value (string expression or literal)
        - An operator (selected from ASSERTION_OPERATOR_LABELS)
        - An optional right-hand value (for non-unary operators)
        - A "soft assertion" flag indicating whether playback should
          continue if the assertion fails

    The dialog initializes its controls from the provided `event` dict,
    specifically from `event["payload"]` if present. When the user
    confirms (OK), the dialog updates `event["payload"]` in-place with
    the edited values and sets `self.changed` to True.

    Unary operators (defined in UNARY_ASSERTION_OPERATORS) do not require a
    right-hand value. When such an operator is selected, the right-hand
    input control is disabled and cleared automatically.

    Parameters
    ----------
    parent : wx.Window
        The parent window.
    event : dict
        The step event dictionary. Its "payload" key will be read and
        updated in-place upon confirmation.

    Attributes
    ----------
    changed : bool
        Indicates whether the user confirmed changes (True after OK).
    """
    # pylint: disable=too-few-public-methods, too-many-instance-attributes

    def __init__(self, parent, event: dict):

        super().__init__(
            parent,
            "Edit Asset Step",
            "Edit Assert Step",
            "Configure how the automation performs assert.")

        self.changed = False
        self._event = event

        payload = AssertPayload(**event.get("payload", {}))

        # Step Label
        self._field_step_label = self.add_field("Step Label:", wx.TextCtrl)
        self._field_step_label.SetValue(payload.label)

        # -- Left Value
        self._field_left = self.add_field("Left Value:", wx.TextCtrl)
        self._field_left.SetValue(payload.left_value)

        # -- Operator
        self._field_operator: wx.Choice = self.add_field(
            "Operator:",
            lambda parent: wx.Choice(parent,
                                     choices=[label for label, _ in \
                                              ASSERTION_OPERATOR_LABELS]))

        # Set existing selection
        for i, (_, op) in enumerate(ASSERTION_OPERATOR_LABELS):
            if op.value == payload.operator:
                self._field_operator.SetSelection(i)
                break
        else:
            self._field_operator.SetSelection(0)

        # -- Right Value
        self._field_right = self.add_field("Right Value:", wx.TextCtrl)
        self._field_right.SetValue("" if not payload.right_value else
                                   payload.right_value)

        # -- Soft Assertion Flag
        self._field_soft_assert = self.add_field("Soft Assert:", wx.CheckBox)
        self._field_soft_assert.SetValue(bool(payload.soft_assert))
        self._field_soft_assert.SetToolTip("Soft assertion (continue on failure)")

        # -- Hint information
        self._field_hint = self.add_full_width_field(
            "",
            lambda parent: wx.StaticText(
                parent,
                label="Use {{property_name}} to reference stored variables."))
        self._field_hint.SetForegroundColour(wx.Colour(120, 120, 120))

        self.finalise()

        self._field_operator.Bind(wx.EVT_CHOICE, self._on_operator_changed)
        self._update_right_enabled()

    def _update_right_enabled(self):

        selected_index = self._field_operator.GetSelection()

        if selected_index == wx.NOT_FOUND:
            self._field_right.Enable(False)
            return

        _, operator = ASSERTION_OPERATOR_LABELS[selected_index]

        self._field_right.Enable(operator not in UNARY_ASSERTION_OPERATORS)

    def _ok_event(self):

        left_value = self._field_left.GetValue().strip()

        selected_index = self._field_operator.GetSelection()
        _, operator = ASSERTION_OPERATOR_LABELS[selected_index]

        payload = {
            "label": self._field_step_label.GetValue(),
            "operator": operator.value,
            "left_value": left_value,
            "soft_assert": self._field_soft_assert.GetValue(),
        }

        right_value = None

        if operator not in UNARY_ASSERTION_OPERATORS:
            right_value = self._field_right.GetValue().strip()
            payload["right_value"] = right_value

        if operator == AssertionOperator.IN:
            try:
                parsed = json.loads(right_value)
            except json.JSONDecodeError:
                wx.MessageBox(
                    "For 'In', the right value must be a valid JSON array.\n"
                    "Example:\n[\"apple\", \"banana\"]",
                    "Validation Error",
                    wx.ICON_WARNING)
                return

            if not isinstance(parsed, list):
                wx.MessageBox(
                    "For 'In', the right value must be a JSON list.",
                    "Validation Error",
                    wx.ICON_WARNING)
                return

        self._event["payload"] = payload

        self.changed = True

    def _on_operator_changed(self, _evt):
        selected_index = self._field_operator.GetSelection()

        if selected_index == wx.NOT_FOUND:
            self._update_right_enabled()
            return

        _, operator = ASSERTION_OPERATOR_LABELS[selected_index]

        if operator in UNARY_ASSERTION_OPERATORS:
            self._field_right.SetValue("")

        if operator == AssertionOperator.IN:
            self._field_hint.SetLabel(
                "Right value must be a JSON array, e.g. "
                "[\"apple\", \"banana\"].")
        else:
            self._field_hint.SetLabel(
                "Use {{property_name}} to reference stored variables.")

        self._update_right_enabled()
