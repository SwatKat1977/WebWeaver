"""
This source file is part of Web Weaver
For the latest info, see https://github.com/SwatKat1977/WebWeaver

Copyright 2025 SwatKat1977

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
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
    NAV_GOTO = "nav.goto"
    DOM_SELECT = "dom.select"
    DOM_TYPE = "dom.type"
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

    if value == "dom.check":
        return RecordingEventType.DOM_CHECK

    if value == "dom.click":
        return RecordingEventType.DOM_CLICK

    if value == "nav.goto":
        return RecordingEventType.NAV_GOTO

    if value == "dom.select":
        return RecordingEventType.DOM_SELECT

    if value == "dom.type":
        return RecordingEventType.DOM_TYPE

    if value == "wait":
        return RecordingEventType.WAIT

    return RecordingEventType.UNKNOWN


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
