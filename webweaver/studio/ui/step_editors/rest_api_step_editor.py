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
from webweaver.studio.persistence.recording_document import RestApiPayload
from webweaver.studio.ui.fancy_dialog_base import FancyDialogBase


class RestApiCallType(Enum):
    """
    Supported HTTP methods for REST API recording steps.

    These values are persisted as lowercase strings in the recording
    document payload.
    """

    GET = "get"
    DELETE = "delete"
    POST = "post"


REST_API_EVENT_TYPE_LABELS: list[tuple[str, RestApiCallType]] = [
    ("GET", RestApiCallType.GET),
    ("DELETE", RestApiCallType.DELETE),
    ("POST", RestApiCallType.POST)
]


class RestApiStepEditor(FancyDialogBase):
    """
    Dialog for creating or editing a REST API playback step.

    The editor allows the user to configure:

    - Base URL
    - HTTP method
    - REST endpoint/path
    - Optional request body (enabled only for POST requests)

    The dialog edits the provided ``event`` dictionary in place. When
    accepted, the updated payload is written back to ``event["payload"]``.

    Attributes:
        changed (bool):
            True if the user confirmed changes with OK.
        _event (dict):
            The recording step event being edited.
    """
    # pylint: disable=too-few-public-methods, too-many-instance-attributes

    def __init__(self, parent, index: int, event: dict):
        """
        Initialize the REST API step editor dialog.

        Args:
            parent:
                Parent wx widget.
            index (int):
                Step index in the recording timeline. Currently unused but
                kept for API consistency with other step editors.
            event (dict):
                Event dictionary containing an optional ``payload`` key.
                The payload is parsed into a ``RestApiPayload`` model and
                written back when saved.
        """
        super().__init__(
            parent,
            "Edit REST API Step",
            "Edit REST API Step",
            "Configure how the automation performs a REST API.")

        self.changed = False
        self._index = index
        self._event = event

        payload = RestApiPayload(**event.get("payload", {}))

        # -- Step Label
        self._field_step_label = self.add_field("Step Label:", wx.TextCtrl)
        self._field_step_label.SetValue(payload.label)

        # -- Base URL
        self._field_base_url = self.add_field("Base URL:", wx.TextCtrl)
        self._field_base_url.SetValue(payload.base_url)

        # -- Call Method
        self._field_call_method: wx.Choice = self.add_field(
            "Call Method:",
            lambda parent: wx.Choice(parent,
                                     choices=[label for label, _ in
                                              REST_API_EVENT_TYPE_LABELS]))

        # Set current call method selection
        current_method = payload.call_type.upper()
        for i, (label, _) in enumerate(REST_API_EVENT_TYPE_LABELS):
            if label == current_method:
                self._field_call_method.SetSelection(i)
                break
        else:
            self._field_call_method.SetSelection(0)

        # -- REST Call
        self._field_rest_call = self.add_field("REST Call:", wx.TextCtrl)
        self._field_rest_call.SetValue(payload.rest_call)

        # -- Output variable
        self._field_output_variable = self.add_field("Output Variable (optional):",
                                                     wx.TextCtrl)
        self._field_output_variable.SetValue(payload.output_variable)

        # -- Call body
        self._field_call_body = self.add_full_width_field(
            "Body (optional):",
            lambda parent: wx.TextCtrl(parent,
                                       value=payload.body or "",
                                       style=wx.TE_MULTILINE))
        self._field_call_body.SetMinSize((450, 150))

        self.finalise()

        self._field_call_method.Bind(wx.EVT_CHOICE, self._on_method_changed)

        self._update_body_enabled()

    def _validate(self):
        """
        Validate inputs and persist dialog values back into the event payload.

        Validation rules:
            - Base URL must not be empty.
            - REST call path must not be empty.

        On success:
            - Updates ``self._event["payload"]``.
            - Sets ``self.changed`` to True.
            - Closes the dialog with ``wx.ID_OK``.
        """
        step_label = self._field_step_label.GetValue()
        base_url = self._field_base_url.GetValue().strip()
        rest_call = self._field_rest_call.GetValue().strip()
        output_variable = self._field_output_variable.GetValue().strip()

        # --- validation ---
        if not base_url:
            wx.MessageBox(
                "Base URL is required.",
                "Validation Error",
                wx.OK | wx.ICON_WARNING)
            self._field_base_url.SetFocus()
            return False

        if not rest_call:
            wx.MessageBox(
                "REST call is required.",
                "Validation Error",
                wx.OK | wx.ICON_WARNING)
            self._field_rest_call.SetFocus()
            return False

        _, enum_val = REST_API_EVENT_TYPE_LABELS[
            self._field_call_method.GetSelection()]

        body_text = self._field_call_body.GetValue().strip()

        self._event["payload"] = {
            "label": step_label,
            "base_url": base_url,
            "call_type": enum_val.value,
            "rest_call": rest_call,
            "output_variable": output_variable,
            "body": body_text or None
        }

        self.changed = True
        return True

    def _update_body_enabled(self):
        """
        Enable or disable the request body control based on method selection.

        The body field is only enabled when POST is selected, reflecting
        the intended use of request payloads within recorded REST steps.
        """
        selected_index = self._field_call_method.GetSelection()

        if selected_index == wx.NOT_FOUND:
            self._field_call_body.Enable(False)
            return

        _, method = REST_API_EVENT_TYPE_LABELS[selected_index]

        self._field_call_body.Enable(method == RestApiCallType.POST)

    def _on_method_changed(self, _evt):
        """
        Handle HTTP method selection changes.

        This updates UI state to ensure controls reflect valid input
        for the selected request type.
        """
        self._update_body_enabled()
