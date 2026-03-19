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
from typing import Callable
import wx
from webweaver.studio.recording.recording_event_type import \
    RecordingEventType
from webweaver.studio.persistence.recording_document import (
    AssertPayload,
    DomCheckPayload,
    DomClickPayload,
    DomGetPayload,
    DomSelectPayload,
    DomTypePayload,
    NavGotoPayload,
    RestApiPayload,
    ScrollPayload,
    SendkeysPayload,
    WaitPayload, UserVariablePayload)


RECORDING_EVENT_TYPE_LABELS: list[tuple[str, RecordingEventType]] = [
    ("Assertion", RecordingEventType.ASSERT),
    ("DOM Click", RecordingEventType.DOM_CLICK),
    ("DOM Get", RecordingEventType.DOM_GET),
    ("DOM Type", RecordingEventType.DOM_TYPE),
    ("DOM Select", RecordingEventType.DOM_SELECT),
    ("DOM Check", RecordingEventType.DOM_CHECK),
    ("Navigate", RecordingEventType.NAV_GOTO),
    ("Rest API", RecordingEventType.REST_API),
    ("Scroll", RecordingEventType.SCROLL),
    ("SendKeys", RecordingEventType.SENDKEYS),
    ("User Variable", RecordingEventType.USER_VARIABLE),
    ("Wait", RecordingEventType.WAIT),
]
"""
Mapping of human-readable step type labels to their corresponding
RecordingEventType enum values.

Used to populate UI selection controls and translate between
display names and internal event types.
"""


def default_payload_for(event_type: RecordingEventType):
    """
    Create a default payload instance appropriate for the given event type.

    Each supported RecordingEventType is mapped to a corresponding
    payload dataclass with sensible default values.

    Args:
        event_type (RecordingEventType):
            The type of event for which to generate a default payload.

    Returns:
        An instance of the payload dataclass associated with the event type.

    Raises:
        ValueError:
            If the provided event type is not supported.
    """

    payload_factories: dict[RecordingEventType, Callable[[], object]] = {
        RecordingEventType.ASSERT: lambda: AssertPayload(label="",
                                                         operator="is_equal_to",
                                                         left_value="",
                                                         right_value=""),
        RecordingEventType.DOM_CLICK: lambda: DomClickPayload(label="",
                                                              xpath=""),
        RecordingEventType.DOM_GET: lambda: DomGetPayload(label="",
                                                          xpath="",
                                                          property_type="text",
                                                          output_variable=""),
        RecordingEventType.DOM_TYPE: lambda: DomTypePayload(label="",
                                                            xpath="", value=""),
        RecordingEventType.DOM_SELECT: lambda: DomSelectPayload(label="",
                                                                xpath="",
                                                                value=""),
        RecordingEventType.DOM_CHECK: lambda: DomCheckPayload(label="",
                                                              xpath="",
                                                              value=True),
        RecordingEventType.NAV_GOTO: lambda: NavGotoPayload(label="",
                                                            url=""),
        RecordingEventType.REST_API: lambda: RestApiPayload(
            label="",
            base_url="",
            call_type="GET",
            rest_call="",
            output_variable="",
            body=""
        ),
        RecordingEventType.SCROLL: lambda: ScrollPayload(label="",
                                                         scroll_type="custom",
                                                         x_scroll=0,
                                                         y_scroll=0),
        RecordingEventType.SENDKEYS: lambda: SendkeysPayload(label="",
                                                             target="",
                                                             keys=[],
                                                             raw_mode=False),
        RecordingEventType.USER_VARIABLE: lambda: UserVariablePayload(label="",
                                                                      name="",
                                                                      value=""),
        RecordingEventType.WAIT: lambda: WaitPayload(label="",
                                                     duration_ms=1000),
    }

    try:
        return payload_factories[event_type]()
    except KeyError as ex:
        raise ValueError(f"Unsupported event type: {event_type}") from ex


class AddStepDialog(wx.Dialog):
    """
    Dialog window used to create a new recording step.

    Presents the user with a dropdown list of available event types
    and returns the selected type when confirmed.
    """
    # pylint: disable=too-few-public-methods

    def __init__(self, parent):
        """
        Initialize the AddStepDialog.

        Args:
            parent: The parent wxPython window.
        """
        super().__init__(parent, title="Add Step")

        self._choices = RECORDING_EVENT_TYPE_LABELS

        self.type_choice = wx.Choice(
            self,
            choices=[label for label, _ in self._choices])
        self.type_choice.SetSelection(0)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(wx.StaticText(self, label="Step type:"), 0, wx.ALL, 5)
        sizer.Add(self.type_choice, 0, wx.EXPAND | wx.ALL, 5)
        sizer.Add(
            self.CreateButtonSizer(wx.OK | wx.CANCEL),
            0,
            wx.ALL | wx.ALIGN_RIGHT,
            10)

        self.SetSizerAndFit(sizer)

    def get_event_type(self) -> RecordingEventType:
        """Return the event type selected by the user.

        Returns:
            The RecordingEventType corresponding to the current
            selection in the dialog.
        """
        _, event_type = self._choices[self.type_choice.GetSelection()]
        return event_type
