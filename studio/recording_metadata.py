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
from __future__ import annotations
import json
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional


class RecordingLoadError(Enum):
    """
    Enumerates possible errors that can occur when loading a recording
    metadata (.wwrec) file.

    This enum mirrors the C++ RecordingLoadError and is intended to allow
    callers to distinguish between different failure modes and present
    appropriate user-facing messages.
    """

    NONE = "none"
    """No error occurred; the recording was loaded successfully."""

    FILE_MALFORMED = "file_malformed"
    """
    The recording metadata file exists but could not be parsed as valid JSON.
    """

    MISSING_RECORDING_OBJECT = "missing_recording_object"
    """The JSON file does not contain a valid top-level 'recording' object."""

    MISSING_REQUIRED_FIELD = "missing_required_field"
    """The 'recording' object is missing one or more required fields."""

    UNSUPPORTED_VERSION = "unsupported_version"
    """The recording metadata version is not supported by this application."""

    FILE_NOT_FOUND = "file_not_found"
    """The recording metadata file does not exist on disk."""


@dataclass
class RecordingLoadResult:
    """
    Represents the result of attempting to load recording metadata.

    This acts as a lightweight result container, holding either a successfully
    loaded RecordingMetadata instance or an error describing why loading failed.
    """

    recording: Optional["RecordingMetadata"] = None
    """
    The loaded recording metadata if loading succeeded, otherwise None.
    """

    error: RecordingLoadError = RecordingLoadError.NONE
    """
    The error encountered during loading, or RecordingLoadError.NONE on success.
    """


@dataclass
class RecordingMetadata:
    """
    Represents metadata associated with a Web Weaver recording (.wwrec file).

    This class encapsulates both the in-memory representation of recording
    metadata and helper methods for loading and updating that metadata on disk.
    """

    id: str
    """Unique identifier for the recording."""

    name: str
    """Human-readable name of the recording."""

    file_path: Path
    """Filesystem path to the .wwrec file backing this metadata."""

    created_at: datetime
    """Timestamp indicating when the recording was created."""

    @staticmethod
    def from_file(wwrec_file: Path) -> RecordingLoadResult:
        """
        Load recording metadata from a .wwrec file.

        The method performs basic validation of the file structure and required
        fields. On failure, no exception is raised; instead, an appropriate
        RecordingLoadError is returned.

        Parameters
        ----------
        wwrec_file : Path
            Path to the .wwrec recording metadata file.

        Returns
        -------
        RecordingLoadResult
            A result object containing either the loaded RecordingMetadata or
            an error describing why loading failed.
        """
        if not wwrec_file.exists():
            return RecordingLoadResult(
                error=RecordingLoadError.FILE_NOT_FOUND
            )

        try:
            with wwrec_file.open("r", encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, json.JSONDecodeError):
            return RecordingLoadResult(
                error=RecordingLoadError.FILE_MALFORMED
            )

        recording = data.get("recording")
        if not isinstance(recording, dict):
            return RecordingLoadResult(
                error=RecordingLoadError.MISSING_RECORDING_OBJECT
            )

        if not all(k in recording for k in ("id", "name", "createdAt")):
            return RecordingLoadResult(
                error=RecordingLoadError.MISSING_REQUIRED_FIELD
            )

        # Placeholder logic preserved from C++
        created_at = datetime.now()

        meta = RecordingMetadata(
            id=str(recording["id"]),
            name=str(recording["name"]),
            file_path=wwrec_file,
            created_at=created_at,
        )

        return RecordingLoadResult(
            recording=meta,
            error=RecordingLoadError.NONE
        )

    def update_recording_name(self) -> bool:
        """
        Update the recording name inside the backing .wwrec file.

        This method reads the existing JSON file, updates the 'name' field of
        the 'recording' object, and writes the file back to disk.

        Returns
        -------
        bool
            True if the file was successfully updated, False otherwise.
        """

        try:
            with self.file_path.open("r", encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, json.JSONDecodeError):
            return False

        if "recording" not in data or not isinstance(data["recording"], dict):
            return False

        data["recording"]["name"] = self.name

        try:
            with self.file_path.open("w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
        except (OSError, TypeError, ValueError):
            return False

        return True

def recording_load_error_to_str(error: RecordingLoadError) -> str:
    """
    Convert a RecordingLoadError into a user-facing error message.

    Args:
        error:
            The recording load error enum value.

    Returns:
        A human-readable description of the recording load error.
        Returns an empty string if the error is unrecognized.
    """
    if error == RecordingLoadError.FILE_MALFORMED:
        return "Recording metadata is malformed."

    if error == RecordingLoadError.MISSING_RECORDING_OBJECT:
        return "Recording metadata missing 'recording' JSON field."

    if error == RecordingLoadError.MISSING_REQUIRED_FIELD:
        return "Recording metadata missing required JSON field."

    if error == RecordingLoadError.UNSUPPORTED_VERSION:
        return "Recording metadata has unsupported version."

    if error == RecordingLoadError.FILE_NOT_FOUND:
        return "Recording metadata file was not found."

    return ""
