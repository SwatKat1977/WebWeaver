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
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
import logging
from pathlib import Path
from typing import Optional
from webweaver.studio.persistence.recording_document import RecordingDocument
from webweaver.studio.persistence.recording_persistence import RecordingPersistence
from webweaver.studio.recording.recording_event_type import RecordingEventType
from webweaver.studio.recording.recording_session import RecordingSession
from webweaver.studio.recording_metadata import RecordingMetadata
from webweaver.studio.solution_coordinator import SolutionCoordinator


class RecordingCoordinator:
    """
    Owns the domain logic for the recording lifecycle and CRUD operations.

    The coordinator has no wx dependencies — all dialogs and UI updates are
    the caller's responsibility.  Methods return plain ``(ok, error_message)``
    tuples so the frame can decide how to surface failures.
    """

    def __init__(self,
                 solution_coordinator: SolutionCoordinator,
                 logger: logging.Logger) -> None:
        self._solution_coordinator = solution_coordinator
        self._logger = logger

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def session(self) -> Optional[RecordingSession]:
        """The active recording session, or None."""
        return self._solution_coordinator.recording_session

    # ------------------------------------------------------------------
    # Session operations
    # ------------------------------------------------------------------

    def start(self) -> tuple[bool, str]:
        """Start a new recording session for the current solution.

        The recording name is generated automatically from the solution's
        existing recordings.

        Returns:
            ``(True, "")`` on success, or ``(False, error_message)`` on failure.
        """
        solution = self._solution_coordinator.current_solution
        if not solution:
            return False, "No solution is loaded."

        session = self._solution_coordinator.recording_session
        if not session:
            return False, "No recording session is available."

        name = solution.generate_next_recording_name()
        ok = session.start(name)
        if not ok:
            return False, session.last_error or "Failed to start recording."
        return True, ""

    def start_existing(self, doc: RecordingDocument) -> tuple[bool, str]:
        """Resume recording into an existing recording document.

        Returns:
            ``(True, "")`` on success, or ``(False, error_message)`` on failure.
        """
        session = self._solution_coordinator.recording_session
        if not session:
            return False, "No recording session is available."

        ok = session.start_existing(doc)
        if not ok:
            return False, session.last_error or "Failed to resume recording."
        return True, ""

    def stop(self) -> tuple[bool, str]:
        """Stop the active recording session.

        Returns:
            ``(True, "")`` on success, or ``(False, error_message)`` on failure.
        """
        session = self._solution_coordinator.recording_session
        if not session:
            return False, "No recording session is available."

        ok = session.stop()
        if not ok:
            return False, session.last_error or "Failed to stop recording."
        return True, ""

    # ------------------------------------------------------------------
    # CRUD operations
    # ------------------------------------------------------------------

    def rename(self,
               recording: RecordingMetadata,
               new_name: str) -> tuple[bool, str]:
        """Rename a recording and persist the updated metadata to disk.

        Returns:
            ``(True, "")`` on success, or ``(False, error_message)`` on failure.
        """
        recording.name = new_name
        if not recording.update_recording_name():
            return False, "Failed to save recording metadata."
        return True, ""

    def delete(self, path: Path) -> tuple[bool, str]:
        """Delete a recording file from disk.

        Returns:
            ``(True, "")`` on success, or ``(False, error_message)`` on failure.
        """
        try:
            path.unlink()
            return True, ""
        except OSError as exc:
            return False, f"Failed to delete recording:\n{exc}"

    def load_document(self, file_path) -> Optional[RecordingDocument]:
        """Load a RecordingDocument from disk.

        Returns the document, or None if the file cannot be loaded.
        """
        return RecordingPersistence.load_from_disk(file_path)

    # ------------------------------------------------------------------
    # Event processing
    # ------------------------------------------------------------------

    def flush_browser_events(self, raw_events: list) -> None:
        """Append a batch of raw browser events to the active recording session.

        Each event dict must contain a ``__kind`` key (``"click"``, ``"type"``,
        ``"check"``, or ``"select"``).  Events without a recognised kind are
        silently ignored.  The ``__kind`` and ``time`` keys are removed from
        the payload before storage.

        Does nothing if no session is active or recording is not running.
        """
        session = self._solution_coordinator.recording_session
        if not session or not session.is_recording():
            return

        for ev in raw_events:
            kind = ev.pop("__kind", None)
            ev.pop("time", None)

            if kind == "click":
                session.append_event(RecordingEventType.DOM_CLICK, payload=ev)
            elif kind == "type":
                session.append_event(RecordingEventType.DOM_TYPE, payload=ev)
            elif kind == "check":
                session.append_event(RecordingEventType.DOM_CHECK, payload=ev)
            elif kind == "select":
                session.append_event(RecordingEventType.DOM_SELECT, payload=ev)

            self._logger.debug("Recorded event: %s", ev)
