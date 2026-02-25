"""
This source file is part of Web Weaver
For the latest info, see https://github.com/SwatKat1977/WebWeaver

Copyright 2025-2026 Webweaver Development Team

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
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Optional
from webweaver.studio.recording.recording_event_type import RecordingEventType


@dataclass
class DomPayload:
    """Base payload for DOM-related events.

    Attributes:
        xpath: XPath expression identifying the target DOM element.
    """
    xpath: str

@dataclass
class AssertPayload:
    """
    Structured payload for an assertion step.

    This dataclass represents the serialized data required to evaluate
    an assertion during playback. It is typically stored within a step
    event and edited via the AssertionStepEditor dialog.

    Fields
    ------
    operator : str
        The string value of the assertion operator (corresponding to
        `AssertionOperator.value`). Determines how the comparison is
        performed.

    left_value : str
        The primary expression or literal being evaluated.

    right_value : str | None
        The secondary value used for binary operators. This should be
        None for unary operators (e.g., IS_TRUE, IS_NONE).

    soft_assert : bool
        If True, a failed assertion will be recorded but will not stop
        playback execution.

    Notes
    -----
    This structure is intentionally serialization-friendly and mirrors
    the shape of the event["payload"] dictionary used in step storage.
    """
    operator: str = "is_equal_to"
    left_value: str = ""
    right_value: None | str = None
    soft_assert: bool = False

@dataclass
class DomCheckPayload(DomPayload):
    """Payload for a DOM checkbox or toggle action.

    Attributes:
        xpath: XPath expression identifying the target element.
        value: Whether the element should be checked (True) or unchecked (False).
    """
    value: bool
    control_type: str = "checkbox"


@dataclass
class DomClickPayload(DomPayload):
    """Payload for a DOM click action.

    Attributes:
        xpath: XPath expression identifying the element to be clicked.
    """
    control_type: str = "click"


@dataclass
class DomGetPayload(DomPayload):
    """
    Payload for a DOM_GET recording step.

    Represents an operation that retrieves a property from a DOM element
    identified by the inherited XPath and stores the result into a named
    output variable for later steps to consume.

    Attributes:
        property_type (str):
            The type of property to retrieve from the DOM element.
            Examples include:
                - "text"         → element.textContent / innerText
                - "value"        → input value
                - "attribute:href" → specific attribute
            Interpretation is handled by the playback engine.

        output_variable (str):
            The name of the variable where the retrieved value will be stored.
            This variable becomes available to subsequent recording steps.
    """
    property_type: str
    output_variable: str


@dataclass
class DomSelectPayload(DomPayload):
    """Payload for selecting an option within a DOM element.

    Attributes:
        xpath: XPath expression identifying the select element.
        value: Value or visible text of the option to select.
    """
    value: str
    control_type: str = "select"


@dataclass
class DomTypePayload(DomPayload):
    """Payload for typing text into a DOM element.

    Attributes:
        xpath: XPath expression identifying the input element.
        value: Text value to be entered into the element.
    """
    value: str
    control_type: str = "text"


@dataclass
class NavGotoPayload:
    """Payload for a navigation action.

    Attributes:
        url: The URL to navigate to.
    """
    url: str


@dataclass
class WaitPayload:
    """Payload representing a timed wait step.

    Attributes:
        duration_ms: Amount of time to wait, in milliseconds.
    """
    duration_ms: int


@dataclass
class RestApiPayload:
    """
    Represents the data required to execute a REST API request.

    This payload object is typically used to describe an API call in a
    serialisable and transport-friendly way (e.g., recording, replaying,
    or passing request definitions between components).

    Attributes:
        base_url (str):
            Root URL of the target API service
            (e.g. ``"https://api.example.com"``).

        call_type (str):
            HTTP method to use for the request.
            Common values include ``"GET"``, ``"POST"``,
            ``"PATCH"``, ``"DELETE"``, etc.

        output_variable (str):
            Optional output variable name.
            Example: `backend_call`.

        rest_call (str):
            Endpoint path appended to ``base_url``.
            Example: ``"/users/123"``.

        body (str | None):
            Optional request body payload, usually JSON-encoded text.
            ``None`` indicates that no body is sent.
    """
    base_url: str
    call_type: str
    rest_call: str
    output_variable: str | None = None
    body: str | None = None


@dataclass
class ScrollPayload:
    """
    Describes a scrolling action for UI or automation workflows.

    This payload captures both the type of scrolling action and
    optional horizontal/vertical scroll values.

    Attributes:
        scroll_type (str):
            Type of scroll action being performed.
            Examples might include ``"absolute"``, ``"relative"``,
            ``"wheel"``, or other system-defined scroll behaviours.

        x_scroll (int | None):
            Horizontal scroll amount. Positive and negative values
            indicate direction depending on the implementation.
            ``None`` if not applicable.

        y_scroll (int | None):
            Vertical scroll amount. Positive and negative values
            indicate direction depending on the implementation.
            ``None`` if not applicable.
    """
    scroll_type: str
    x_scroll: int | None = None
    y_scroll: int | None = None


class RecordingDocument:
    """
    File-backed document model representing a loaded recording.

    A RecordingDocument binds together:
    - The on-disk path of a recording file (e.g. a .wwrec file)
    - The full parsed JSON data structure loaded from that file

    This class acts as the authoritative, in-memory representation of a
    recording document as it exists on disk. It does not interpret or
    manipulate the contents of the recording; it simply owns:

        - Where the recording came from (path)
        - What the recording contains (raw data)

    Higher-level layers (e.g. RecordingViewContext, playback systems, editors)
    should treat this object as the immutable source of truth for persistence
    and saving.

    This mirrors the concept of a "document" in editors like VSCode:
    the document is the file + its loaded contents, not the UI view of it.
    """
    __slots__ = ["_path", "_recording_data"]

    DEFAULT_STEP_GAP_MS = 1000

    def __init__(self, path: Path, recording_data: dict):
        """
        Create a new RecordingDocument.

        :param path: Path to the recording file on disk.
        :param recording_data: Parsed JSON data loaded from the recording file.
        """
        self._path = path
        self._recording_data = recording_data

    @property
    def path(self) -> Path:
        """
        Get the filesystem path of this recording document.

        :return: Path to the recording file on disk.
        """
        return self._path

    @property
    def data(self) -> dict:
        """
        Get the raw recording data.

        This is the full JSON-compatible dictionary loaded from disk, including
        metadata and event lists.

        :return: Recording data dictionary.
        """
        return self._recording_data

    def get_step(self, index: int) -> dict:
        """
        Retrieve a single recording step by index.

        This returns the raw event dictionary from the underlying recording
        data structure.

        :param index: Zero-based index of the step to retrieve.
        :return: The event dictionary at the given index.
        :raises IndexError: If the index is out of range.
        """
        return self._recording_data["recording"]["events"][index]

    def delete_step(self, index: int) -> None:
        """
        Delete a recording step by index.

        If the index is out of range, this method does nothing.

        After deletion, all remaining steps are reindexed so their "index"
        fields remain contiguous and consistent with their position in the
        events list.

        :param index: Zero-based index of the step to delete.
        """
        events = self._recording_data["recording"]["events"]

        if index < 0 or index >= len(events):
            return

        del events[index]

        # Reindex
        for i, ev in enumerate(events):
            ev["index"] = i

    def move_step(self, from_index: int, to_index: int) -> bool:
        """Move a recording step to a new position in the event list.

        The step at the specified source index is removed and reinserted
        at the destination index. All events are reindexed after the move
        to maintain sequential ordering.

        Args:
            from_index: The current index of the step to move.
            to_index: The target index where the step should be placed.

        Returns:
            True if the step was successfully moved, or False if either
            index was out of range.
        """
        events = self._recording_data["recording"]["events"]

        if from_index < 0 or from_index >= len(events):
            return False
        if to_index < 0 or to_index >= len(events):
            return False

        step = events.pop(from_index)
        events.insert(to_index, step)

        for i, ev in enumerate(events):
            ev["index"] = i

        return True

    def insert_step_after(
            self,
            index: Optional[int],
            event_type: RecordingEventType,
            payload: DomPayload,
    ) -> int:
        """Insert a new step into the recording after the given index.

        A new event dictionary is created using the provided event type
        and payload, and inserted immediately after the specified index.
        If no index is provided, the step is appended to the end of the
        event list. All events are reindexed and timestamps are
        renormalized after insertion.

        Args:
            index: The index after which the new step should be inserted.
                If None, the step is added to the end of the recording.
            event_type: The type of event to create.
            payload: The payload data associated with the new event.

        Returns:
            The index at which the new step was inserted.
        """
        events = self._recording_data["recording"]["events"]
        insert_index = len(events) if index is None else index + 1
        insert_index = min(insert_index, len(events))

        event: dict = {
            "index": insert_index,
            "timestamp": 11123,
            "type": event_type.value,
            "payload": asdict(payload)
        }

        events.insert(insert_index, event)

        # Reindex
        for i, ev in enumerate(events):
            ev["index"] = i

        self._renormalise_timestamps()

        return insert_index

    def _renormalise_timestamps(self) -> None:
        """
        Renormalise step timestamps to maintain monotonic ordering
        after structural edits (insert, delete, move).

        Timestamps are treated as derived data and are reassigned
        sequentially based on step order.
        """
        events = self._recording_data["recording"]["events"]

        for i, ev in enumerate(events):
            ev["timestamp"] = i * self.DEFAULT_STEP_GAP_MS
