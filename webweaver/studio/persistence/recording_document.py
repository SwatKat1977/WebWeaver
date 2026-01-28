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
from pathlib import Path


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
