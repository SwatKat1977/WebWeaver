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

class AssertionOperator(str, Enum):
    """
    Enumeration of supported assertion operators.

    Each operator defines the comparison or validation rule applied
    during assertion step execution. The enum inherits from `str`
    so that values can be serialized directly (e.g., into JSON) and
    persisted in step payloads without additional conversion.

    Categories
    ----------
    Binary operators (require left and right values):
        - EQUALS
        - NOT_EQUALS
        - GREATER_THAN
        - LESS_THAN
        - CONTAINS
        - IN
        - STARTS_WITH
        - ENDS_WITH
        - MATCHES_REGEX

    Unary operators (require only a left value):
        - IS_TRUE
        - IS_FALSE
        - IS_NONE
        - IS_NOT_NONE

    Notes
    -----
    Operators listed as unary should also be included in
    `UNARY_OPERATORS` to ensure UI components (such as
    AssertionStepEditor) correctly disable the right-hand input.
    """
    EQUALS = "equals"
    NOT_EQUALS = "not_equals"
    GREATER_THAN = "greater_than"
    LESS_THAN = "less_than"
    CONTAINS = "contains"
    IN = "in"
    STARTS_WITH = "starts_with"
    ENDS_WITH = "ends_with"
    MATCHES_REGEX = "matches_regex"
    IS_TRUE = "is_true"
    IS_FALSE = "is_false"
    IS_NONE = "is_none"
    IS_NOT_NONE = "is_not_none"

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
UNARY_OPERATORS = {
    AssertionOperator.IS_TRUE,
    AssertionOperator.IS_FALSE,
    AssertionOperator.IS_NONE,
    AssertionOperator.IS_NOT_NONE,
}

class AssertionStepEditor(wx.Dialog):
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

    Unary operators (defined in UNARY_OPERATORS) do not require a
    right-hand value. When such an operator is selected, the right-hand
    input control is disabled and cleared automatically.

    Parameters
    ----------
    parent : wx.Window
        The parent window.
    _index : int
        The index of the step being edited (currently unused but kept
        for interface consistency with other step editors).
    event : dict
        The step event dictionary. Its "payload" key will be read and
        updated in-place upon confirmation.

    Attributes
    ----------
    changed : bool
        Indicates whether the user confirmed changes (True after OK).
    """
    # pylint: disable=too-few-public-methods

    def __init__(self, parent, _index: int, event: dict):
        super().__init__(parent, title="Edit Assertion Step")

        self.changed = False
        self._event = event

        payload = event.get("payload", {})

        # ----------------------------
        # Controls
        # ----------------------------

        self._left_ctrl = wx.TextCtrl(
            self,
            value=payload.get("left_value", "")
        )

        self._operator_choice = wx.Choice(
            self,
            choices=[label for label, _ in ASSERTION_OPERATOR_LABELS]
        )

        self._right_ctrl = wx.TextCtrl(
            self,
            value=payload.get("right_value", "")
        )

        self._soft_checkbox = wx.CheckBox(
            self,
            label="Soft assertion (continue on failure)"
        )
        self._soft_checkbox.SetValue(payload.get("soft_assert", False))

        self._hint_label = wx.StaticText(
            self,
            label="Use {{property_name}} to reference stored variables."
        )
        self._hint_label.SetForegroundColour(wx.Colour(120, 120, 120))

        # ----------------------------
        # Set existing selection
        # ----------------------------

        current_operator = payload.get("operator")

        for i, (_, op) in enumerate(ASSERTION_OPERATOR_LABELS):
            if op.value == current_operator:
                self._operator_choice.SetSelection(i)
                break
        else:
            self._operator_choice.SetSelection(0)

        # ----------------------------
        # Layout
        # ----------------------------

        main_sizer = wx.BoxSizer(wx.VERTICAL)

        form = wx.FlexGridSizer(cols=2, hgap=8, vgap=12)
        form.AddGrowableCol(1, 1)

        # Left
        form.Add(wx.StaticText(self, label="Left Value:"),
                 0, wx.ALIGN_CENTER_VERTICAL)
        form.Add(self._left_ctrl, 1, wx.EXPAND)

        # Operator
        form.Add(wx.StaticText(self, label="Operator:"),
                 0, wx.ALIGN_CENTER_VERTICAL)
        form.Add(self._operator_choice, 1, wx.EXPAND)

        # Right
        form.Add(wx.StaticText(self, label="Right Value:"),
                 0, wx.ALIGN_CENTER_VERTICAL)
        form.Add(self._right_ctrl, 1, wx.EXPAND)

        # Soft assertion flag

        main_sizer.Add(form, 0, wx.EXPAND | wx.ALL, 15)
        form.Add(self._soft_checkbox,
                       0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)
        main_sizer.Add(self._hint_label, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)
        main_sizer.Add(self.CreateButtonSizer(wx.OK | wx.CANCEL),
                       0, wx.ALL | wx.ALIGN_RIGHT, 10)

        self.SetSizer(main_sizer)
        self.Fit()
        self.CentreOnParent()

        # ----------------------------
        # Bindings
        # ----------------------------
        self.Bind(wx.EVT_BUTTON, self._on_ok, id=wx.ID_OK)
        self._operator_choice.Bind(wx.EVT_CHOICE, self._on_operator_changed)

        self._update_right_enabled()

    def _update_right_enabled(self):

        selected_index = self._operator_choice.GetSelection()

        if selected_index == wx.NOT_FOUND:
            self._right_ctrl.Enable(False)
            return

        _, operator = ASSERTION_OPERATOR_LABELS[selected_index]

        self._right_ctrl.Enable(operator not in UNARY_OPERATORS)

    def _on_ok(self, _evt):

        left_value = self._left_ctrl.GetValue().strip()

        selected_index = self._operator_choice.GetSelection()
        _, operator = ASSERTION_OPERATOR_LABELS[selected_index]

        payload = {
            "operator": operator.value,
            "left_value": left_value,
            "soft_assert": self._soft_checkbox.GetValue(),
        }

        if operator not in UNARY_OPERATORS:
            right_value = self._right_ctrl.GetValue().strip()
            payload["right_value"] = right_value

        self._event["payload"] = payload

        self.changed = True
        self.EndModal(wx.ID_OK)

    def _on_operator_changed(self, _evt):
        selected_index = self._operator_choice.GetSelection()
        if selected_index != wx.NOT_FOUND:
            _, operator = ASSERTION_OPERATOR_LABELS[selected_index]
            if operator in UNARY_OPERATORS:
                self._right_ctrl.SetValue("")

        self._update_right_enabled()
