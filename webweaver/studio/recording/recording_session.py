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
from datetime import datetime, timezone
import json
from pathlib import Path
import time
import typing
import uuid
from recording.recording_event_type import RecordingEventType
from studio_solution import StudioSolution


def now_utc_iso() -> str:
    """
    Get the current UTC time formatted as an ISO-8601 timestamp string.

    The returned string is in the format:

        YYYY-MM-DDTHH-MM-SS

    This format is suitable for use in filenames and JSON metadata where
    a stable, timezone-independent timestamp is required.

    Returns
    -------
    str
        The current UTC time formatted as an ISO-8601 string.
    """
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%S")


class RecordingSession:
    """
    Manages a live recording session for a solution.

    This class is responsible for creating, writing, and finalizing a recording
    file (.wwrec). It handles session lifecycle, event indexing, timestamping,
    and incremental persistence to disk.

    A recording session is started with :meth:`start`, populated with events
    using :meth:`append_event`, and finalized using :meth:`stop`.
    """

    def __init__(self, solution: StudioSolution):
        """
        Create a new RecordingSession.

        Parameters
        ----------
        solution : StudioSolution
            The solution for which this recording session is created.
        """
        self._active: bool = False
        self._file_path: typing.Optional[Path] = None
        self._recording_json: typing.Dict[str, typing.Any] = {}
        self._next_index: int = 0
        self._start_time: typing.Optional[float] = None
        self._solution = solution
        self._last_error: typing.Optional[str] = None

    @property
    def last_error(self) -> typing.Optional[str]:
        """ Get the last error message, or None if no message """
        return self._last_error

    def is_recording(self) -> bool:
        """
        Check whether a recording session is currently active.

        Returns
        -------
        bool
            True if a recording is currently in progress, False otherwise.
        """
        return self._active

    def start(self, name: str) -> bool:
        """
        Start a new recording session.

        This creates a new recording file in the solution's recordings
        directory, initializes the recording metadata, and writes the initial
        file to disk.

        Parameters
        ----------
        name : str
            Human-readable name of the recording.

        Returns
        -------
        bool
            True if the recording session was started successfully, or False
            if a session is already active or the file could not be created.
        """
        self._last_error = None

        if self._active:
            self._last_error = "A recording session is already active."
            return False

        recordings_dir = self._solution.get_recordings_directory()
        recordings_dir.mkdir(parents=True, exist_ok=True)

        filename: str = f"{name}_{now_utc_iso()}.wwrec"
        self._file_path = recordings_dir / filename

        recording_id = str(uuid.uuid4())

        self._recording_json = {
            "version": 1,
            "recording": {
                "id": recording_id,
                "name": name,
                "createdAt": now_utc_iso(),
                "browser": self._solution.selected_browser,
                "baseUrl": self._solution.base_url,
                "events": []
            }
        }

        try:
            self._flush_to_disk()

        except OSError as ex:
            self._last_error = f"Failed to create recording file:\n{ex}"
            return False

        self._active = True
        self._next_index = 0
        self._start_time = time.monotonic()

        return True

    def stop(self) -> bool:
        """
        Stop the active recording session.

        Finalizes the recording by writing the end timestamp and flushing
        the final state to disk. If no recording is active, this method does
        nothing.
        """
        if not self._active:
            return False

        self._recording_json["recording"]["endedAt"] = now_utc_iso()

        # Persist final state
        self._flush_to_disk()
        self._active = False

        return True

    def append_event(self,
                     event_type: RecordingEventType,
                     payload: typing.Dict[str, typing.Any]) -> None:
        """
        Append a single event to the active recording.

        - The event index and timestamp are assigned automatically.
        - Events are always appended in chronological order.
        - Each call immediately persists the updated recording to disk.

        This method also:
        - Coalesces consecutive DOM_TYPE / DOM_SELECT / DOM_CHECK on same element
        - Suppresses useless layout clicks
        - Removes click events that are immediately followed by select/check

        If no recording session is currently active, this method does nothing.
        """
        if not self._active or self._start_time is None:
            return

        elapsed_ms: int = int((time.monotonic() - self._start_time) * 1000)

        events = self._recording_json["recording"]["events"]

        selector = (payload.get("selector") or "").lower()

        # ------------------------------------------------------------
        # 1) Drop useless clicks on layout / non-interactive elements
        # ------------------------------------------------------------
        if event_type == RecordingEventType.DOM_CLICK:
            # Very simple heuristic for now (we can refine later)
            if (
                    selector.startswith("div") or
                    selector.startswith("span") or
                    selector.startswith("h") or
                    selector.startswith("p")
            ):
                return

            # Only keep clicks that look like real actions
            if not (
                    selector.startswith("button") or
                    selector.startswith("a") or
                    "button" in selector
            ):
                return

        # ------------------------------------------------------------
        # 2) If this is SELECT or CHECK, and last event was CLICK
        #    on same element -> remove the click
        # ------------------------------------------------------------
        if event_type in (RecordingEventType.DOM_SELECT, RecordingEventType.DOM_CHECK):
            if events:
                last = events[-1]
                if (
                        last["type"] == RecordingEventType.DOM_CLICK.value and
                        last["payload"].get("selector") == payload.get("selector")
                ):
                    events.pop()
                    self._next_index -= 1

        # ------------------------------------------------------------
        # 3) Coalesce logic (your existing logic, unchanged)
        # ------------------------------------------------------------
        if events:
            last = events[-1]

            if event_type in (
                    RecordingEventType.DOM_TYPE,
                    RecordingEventType.DOM_SELECT,
                    RecordingEventType.DOM_CHECK,
            ):
                if (
                        last["type"] == event_type.value and
                        last["payload"].get("selector") == payload.get("selector")
                ):
                    # Replace last event instead of appending
                    last["timestamp"] = elapsed_ms
                    last["payload"] = payload

                    self._flush_to_disk()
                    return

        # ------------------------------------------------------------
        # 4) Normal append
        # ------------------------------------------------------------
        event = {
            "index": self._next_index,
            "timestamp": elapsed_ms,
            "type": event_type.value,
            "payload": payload
        }

        self._next_index += 1
        events.append(event)

        self._flush_to_disk()

    def _flush_to_disk(self) -> None:
        """
        Write the current recording state to disk.

        This overwrites the recording file with the current JSON state.
        If no file path is set, this method does nothing.
        """
        if self._file_path is None:
            return

        with self._file_path.open("w", encoding="utf-8") as f:
            json.dump(self._recording_json, f, indent=4)
