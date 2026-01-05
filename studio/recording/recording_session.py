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

#include "StudioSolution.h"

def now_utc_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class RecordingSession:
    def __init__(self, solution: StudioSolution):
        self._active: bool = False
        self._file_path: typing.Optional[Path] = None
        self._recording_json: typing.Dict[str, typing.Any] = {}
        self._next_index: int = 0
        self._start_time: typing.Optional[float] = None
        self._solution = solution

    def is_recording(self) -> bool:
        return self._active

    def start(self, name: str) -> bool:
        if self._active:
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

        except OSError:
            return False

        self._active = True
        self._next_index = 0
        self._start_time = time.monotonic()

        return True

    def stop(self):
        if not self._active:
            return

        self._recording_json["recording"]["endedAt"] = now_utc_iso()

        # Persist final state
        self._flush_to_disk()
        self._active = False

    def append_event(self,
                     event_type: RecordingEventType,
                     payload: typing.Dict[str, typing.Any]) -> None:
        """
        Appends a single immutable event to the recording.
        - Index and timestamp are assigned internally.
        - Events are always appended in order.
        - This method is safe to call repeatedly while recording is active.
        """
        if not self._active or self._start_time is None:
            return

        elapsed_ms: int = int((time.monotonic() - self._start_time) * 1000)

        event = {
            "index": self._next_index,
            "timestamp": elapsed_ms,
            "type": event_type.value,
            "payload": payload
        }

        self._next_index += 1
        self._recording_json["recording"]["events"].append(event)

        self._flush_to_disk()

    def _flush_to_disk(self) -> None:
        if self._file_path is None:
            return

        with self._file_path.open("w", encoding="utf-8") as f:
            json.dump(self._recording_json, f, indent=4)
