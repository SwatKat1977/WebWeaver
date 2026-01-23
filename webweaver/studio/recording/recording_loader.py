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
import json
from typing import Optional
from recording_view_context import RecordingViewContext
from recording.recording import Recording


def load_recording_from_context(ctx: RecordingViewContext) -> Optional[Recording]:
    """
    Load a full recording (metadata + events) from disk.
    """
    try:
        with ctx.recording_file.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError):
        return None

    rec = data.get("recording")
    if not isinstance(rec, dict):
        return None

    events = rec.get("events")
    if not isinstance(events, list):
        return None

    return Recording(
        metadata=ctx.metadata,
        events=events)
