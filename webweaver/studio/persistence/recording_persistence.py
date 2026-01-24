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
import json
from pathlib import Path
from persistence.recording_document import RecordingDocument


class RecordingLoadError(Exception):
    """Raised when a recording file cannot be loaded."""
    pass


class RecordingSaveError(Exception):
    """Raised when a recording file cannot be saved."""
    pass


class RecordingPersistence:
    """
    Persistence layer for RecordingDocument objects.

    Responsible for loading and saving recording documents to and from disk.
    """

    @staticmethod
    def load_from_disk(recording_file: Path) -> RecordingDocument:
        """
        Load a recording file from disk and return a RecordingDocument.

        :param recording_file: Path to the .wwrec file.
        :return: RecordingDocument instance.
        :raises RecordingLoadError: If the file cannot be read or parsed.
        """
        try:
            text = recording_file.read_text(encoding="utf-8")
            data = json.loads(text)
            return RecordingDocument(recording_file, data)

        except (OSError, json.JSONDecodeError) as ex:
            raise RecordingLoadError(
                f"Failed to load recording: {recording_file}") from ex

    @staticmethod
    def save_to_disk(recording: RecordingDocument) -> None:
        """
        Save a RecordingDocument back to disk.

        :param recording: RecordingDocument to save.
        :raises RecordingSaveError: If the file cannot be written.
        """
        try:
            recording.path.write_text(
                json.dumps(recording.data, indent=2),
                encoding="utf-8")

        except OSError as ex:
            raise RecordingSaveError(
                f"Failed to save recording: {recording.path}") from ex
