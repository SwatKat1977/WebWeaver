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
import enum


class RecordingEventType(enum.Enum):
    """
    Enumeration of supported recording event types.

    This enum represents the different kinds of events that may appear
    in a recording timeline or event stream. The string values correspond
    to the serialized form used in recording files.
    """

    DOM_CHECK = "dom.check"
    DOM_CLICK = "dom.click"
    DOM_GET = "dom.get"
    DOM_SELECT = "dom.select"
    DOM_TYPE = "dom.type"
    NAV_GOTO = "nav.goto"
    REST_API = "rest_api"
    SCROLL = "scroll"
    WAIT = "wait"
    UNKNOWN = "unknown"


def event_type_from_str(value: str) -> RecordingEventType:
    """
    Convert a string value into a :class:`RecordingEventType`.

    This function maps the serialized string representation of an event
    type (as stored in recording files) to the corresponding enum value.
    If the input string is not recognized, :data:`RecordingEventType.UNKNOWN`
    is returned.

    Parameters
    ----------
    value : str
        Serialized event type string (e.g. ``"nav.goto"``, ``"dom.click"``,
        ``"wait"``).

    Returns
    -------
    RecordingEventType
        The corresponding enum value, or :data:`RecordingEventType.UNKNOWN`
        if the string is not recognized.
    """

    event_type: RecordingEventType = RecordingEventType.UNKNOWN

    if value == "dom.check":
        event_type = RecordingEventType.DOM_CHECK

    elif value == "dom.click":
        event_type = RecordingEventType.DOM_CLICK

    elif value == "nav.goto":
        event_type = RecordingEventType.NAV_GOTO

    elif value == "dom.select":
        event_type = RecordingEventType.DOM_SELECT

    elif value == "dom.type":
        event_type = RecordingEventType.DOM_TYPE

    elif value == "rest_api":
        event_type = RecordingEventType.REST_API

    elif value == "scroll":
        event_type = RecordingEventType.SCROLL

    elif value == "wait":
        event_type = RecordingEventType.WAIT

    return event_type


def event_type_to_str(event_type: RecordingEventType) -> str:
    """
    Convert a :class:`RecordingEventType` into its serialized string form.

    This returns the value that should be written to disk or transmitted
    when serializing a recording event.

    Parameters
    ----------
    event_type : RecordingEventType
        The event type to convert.

    Returns
    -------
    str
        The serialized string representation of the event type.
    """
    return event_type.value
