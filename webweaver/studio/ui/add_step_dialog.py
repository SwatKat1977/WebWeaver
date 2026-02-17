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
import wx
from webweaver.studio.recording.recording_event_type import \
    RecordingEventType
from webweaver.studio.persistence.recording_document import (
                                              DomCheckPayload,
                                              DomClickPayload,
                                              DomSelectPayload,
                                              DomTypePayload,
                                              NavGotoPayload,
                                              RestApiPayload,
                                              WaitPayload)


RECORDING_EVENT_TYPE_LABELS: list[tuple[str, RecordingEventType]] = [
    ("DOM Click", RecordingEventType.DOM_CLICK),
    ("DOM Type", RecordingEventType.DOM_TYPE),
    ("DOM Select", RecordingEventType.DOM_SELECT),
    ("DOM Check", RecordingEventType.DOM_CHECK),
    ("Navigate", RecordingEventType.NAV_GOTO),
    ("Rest API", RecordingEventType.REST_API),
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
        event_type (RecordingEventType): The type of event for which to
            generate a default payload.

    Returns:
        An instance of the payload dataclass associated with the event type.

    Raises:
        ValueError: If the provided event type is not supported.
    """
    if event_type == RecordingEventType.DOM_CLICK:
        return DomClickPayload(xpath="")

    if event_type == RecordingEventType.DOM_TYPE:
        return DomTypePayload(xpath="", value="")

    if event_type == RecordingEventType.DOM_SELECT:
        return DomSelectPayload(xpath="", value="")

    if event_type == RecordingEventType.DOM_CHECK:
        return DomCheckPayload(xpath="", value=True)

    if event_type == RecordingEventType.NAV_GOTO:
        return NavGotoPayload(url="")

    if event_type == RecordingEventType.REST_API:
        return RestApiPayload(base_url="", call_type="GET", call="")

    if event_type == RecordingEventType.WAIT:
        return WaitPayload(duration_ms=1000)

    raise ValueError(f"Unsupported event type: {event_type}")


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
