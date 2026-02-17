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
from enum import Enum
import wx
from webweaver.studio.persistence.recording_document import RestApiPayload


class RestApiCallType(Enum):
    GET = "get"
    DELETE = "delete"
    POST = "post"


REST_API_EVENT_TYPE_LABELS: list[tuple[str, RestApiCallType]] = [
    ("GET", RestApiCallType.GET),
    ("DELETE", RestApiCallType.DELETE),
    ("POST", RestApiCallType.POST)
]


class RestApiStepEditor(wx.Dialog):

    def __init__(self, parent, _index: int, event: dict):
        super().__init__(parent, title="Edit REST API Step")

        self.changed = False
        self._event = event

        payload = RestApiPayload(**event.get("payload", {}))

        # --- controls ---

        # Base URL Control
        self._base_url_ctrl = wx.TextCtrl(
            self,
            value=payload.base_url)

        # REST API Call Control
        self._rest_call_ctrl = wx.TextCtrl(
            self,
            value=payload.rest_call)

        # REST API Call Method Control
        self._method_choice_ctrl = wx.Choice(
            self,
            choices=[label for label, _ in REST_API_EVENT_TYPE_LABELS])

        # Set current selection
        current_method = payload.call_type.upper()
        for i, (label, _) in enumerate(REST_API_EVENT_TYPE_LABELS):
            if label == current_method:
                self._method_choice_ctrl.SetSelection(i)
                break
        else:
            self._method_choice_ctrl.SetSelection(0)

        self._body_ctrl = wx.TextCtrl(
            self,
            value=payload.body or "",
            style=wx.TE_MULTILINE)

        main_sizer = wx.BoxSizer(wx.VERTICAL)

        form = wx.FlexGridSizer(cols=2, hgap=2, vgap=8)
        form.AddGrowableCol(1, 1)

        form.Add(wx.StaticText(self, label="Base URL:"),
                 0, wx.ALIGN_CENTER_VERTICAL)
        form.Add(self._base_url_ctrl, 1, wx.EXPAND)

        form.Add(wx.StaticText(self, label="Call Type:"),
                 0, wx.ALIGN_CENTER_VERTICAL)
        form.Add(self._method_choice_ctrl, 1, wx.EXPAND)

        form.Add(wx.StaticText(self, label="REST Call:"),
                 0, wx.ALIGN_CENTER_VERTICAL)
        form.Add(self._rest_call_ctrl, 1, wx.EXPAND)

        main_sizer.Add(form, 0, wx.EXPAND | wx.ALL, 10)

        main_sizer.Add(wx.StaticText(self, label="Body (optional):"),
                       0,
                       wx.LEFT | wx.RIGHT | wx.TOP,
                       10)
        main_sizer.Add(self._body_ctrl,
                       1,
                       wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM,
                       10)

        main_sizer.Add(self.CreateButtonSizer(wx.OK | wx.CANCEL),
                       0, wx.ALL | wx.ALIGN_RIGHT, 10)

        self.SetSizer(main_sizer)
        self.SetSize((650, 450))
        self.CentreOnParent()

        self.Bind(wx.EVT_BUTTON, self._on_ok, id=wx.ID_OK)
        self._method_choice_ctrl.Bind(wx.EVT_CHOICE, self._on_method_changed)

        self._update_body_enabled()

    def _on_ok(self, _evt):

        label, enum_val = REST_API_EVENT_TYPE_LABELS[
            self._method_choice_ctrl.GetSelection()
        ]

        body_text = self._body_ctrl.GetValue().strip()

        self._event["payload"] = {
            "base_url": self._base_url_ctrl.GetValue(),
            "call_type": enum_val.value,
            "rest_call": self._rest_call_ctrl.GetValue(),
            "body": body_text or None
        }

        self.changed = True
        self.EndModal(wx.ID_OK)

    def _update_body_enabled(self):
        """
        Enable body input only when POST is selected.
        """
        selected_index = self._method_choice_ctrl.GetSelection()

        if selected_index == wx.NOT_FOUND:
            self._body_ctrl.Enable(False)
            return

        _, method = REST_API_EVENT_TYPE_LABELS[selected_index]

        self._body_ctrl.Enable(method == RestApiCallType.POST)

    def _on_method_changed(self, _evt):
        self._update_body_enabled()
