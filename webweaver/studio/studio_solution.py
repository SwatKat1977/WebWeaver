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
import dataclasses
import enum
from pathlib import Path
import typing
import wx
from webweaver.studio.browser_launch_options import BrowserLaunchOptions
from webweaver.studio.recording_metadata import (RecordingMetadata,
                                                 recording_load_error_to_str)
from webweaver.studio.recording_view_context import RecordingViewContext
from webweaver.studio.persistence.solution_persistence import \
    SolutionDirectoryCreateStatus


#: Current .WWS version number
JSON_VERSION: int = 1

#: Subdirectory name for stored pages
PAGES_DIRECTORY: str = "pages"

#: Subdirectory name for stored scripts
SCRIPTS_DIRECTORY: str = "scripts"

#: Subdirectory name for stored recordings
RECORDINGS_DIRECTORY: str = "recordings"

#: Subdirectory name for stored test suites
TEST_SUITES_DIRECTORY: str = "test_suites"


class SolutionLoadError(enum.Enum):
    """
    Enumerates possible errors that may occur while loading a solution file.
    """
    NONE_ = 0
    FILE_MALFORMED = enum.auto()
    MISSING_VERSION = enum.auto()
    UNSUPPORTED_VERSION = enum.auto()
    MISSING_SOLUTION_OBJECT = enum.auto()
    MISSING_REQUIRED_FIELD = enum.auto()


class ScreenshotPolicy(enum.Enum):
    """
    Defines when screenshots should be captured during recording or playback.

    This policy controls the level of visual logging performed for each step
    in a recording. It is typically used by the playback engine to determine
    whether to capture screenshots for debugging, auditing, or reporting
    purposes.

    Attributes:
        OFF: No screenshots are captured at any point.
        ON_FAILURE: Screenshots are captured only when a step fails.
        ALL_STEPS: Screenshots are captured for every step, regardless of
                   outcome.

    Notes:
        - Capturing screenshots for all steps can significantly increase
          storage usage and impact performance.
        - ON_FAILURE is typically a good balance between visibility and
          efficiency.
    """
    OFF = "off"
    ON_FAILURE = "on_failure"
    ALL_STEPS = "all_steps"


@dataclasses.dataclass
class SolutionLoadResult:
    """
    Result container returned when loading a solution from disk.

    Attributes:
        solution:
            The loaded StudioSolution instance, or None if loading failed.
        error:
            A SolutionLoadError describing the failure, or NONE_ on success.
    """
    solution: typing.Optional["StudioSolution"] = None
    error: SolutionLoadError = SolutionLoadError.NONE_


@dataclasses.dataclass
class StudioSolution:
    """
    Represents a WebWeaver Studio solution.

    A solution defines a workspace on disk along with browser configuration
    and recording metadata.
    """
    # pylint: disable=too-many-instance-attributes

    solution_name: str
    solution_directory: str
    create_directory_for_solution: bool
    base_url: str
    selected_browser: str
    launch_browser_automatically: bool
    browser_launch_options: BrowserLaunchOptions
    recordings_cache: typing.Dict[str, RecordingMetadata] = \
        dataclasses.field(default_factory=dict)
    default_screenshots_policy: str = 'off'

    def to_json(self):
        """
        Serialize this solution to a versioned JSON-compatible dictionary.

        Returns:
            A dictionary suitable for JSON encoding and persistence.
        """
        return {
            "version": JSON_VERSION,
            "solution": {
                "solutionName": self.solution_name,
                "solutionDirectoryCreated": self.create_directory_for_solution,
                "baseUrl": self.base_url,
                "browser": self.selected_browser,
                "launchBrowserAutomatically": self.launch_browser_automatically
            },
            "browserLaunchOptions": self.browser_launch_options.to_json(),
            "default_screenshots_policy": self.default_screenshots_policy
        }

    @staticmethod
    def from_json(raw: typing.Any) -> SolutionLoadResult:
        """
        Attempt to deserialize a StudioSolution from raw JSON data.

        Args:
            raw:
                Parsed JSON content (typically a dict).

        Returns:
            A SolutionLoadResult containing either the solution or an error.
        """
        # pylint: disable=too-many-return-statements

        if not isinstance(raw, dict):
            return SolutionLoadResult(None, SolutionLoadError.FILE_MALFORMED)

        if "version" not in raw:
            return SolutionLoadResult(None, SolutionLoadError.MISSING_VERSION)

        if not isinstance(raw["version"], int):
            return SolutionLoadResult(None, SolutionLoadError.FILE_MALFORMED)

        version = raw["version"]
        if version != 1:
            return SolutionLoadResult(None, SolutionLoadError.UNSUPPORTED_VERSION)

        raw_solution = raw.get("solution")
        if not isinstance(raw_solution, dict):
            return SolutionLoadResult(None, SolutionLoadError.MISSING_SOLUTION_OBJECT)

        if "default_screenshots_policy" not in raw:
            raw["default_screenshots_policy"] = "off"

        default_screenshots_policy = raw.get("default_screenshots_policy")

        required = [
            "solutionName",
            "solutionDirectoryCreated",
            "baseUrl",
            "browser",
            "launchBrowserAutomatically",
        ]

        if any(k not in raw_solution for k in required):
            return SolutionLoadResult(None, SolutionLoadError.MISSING_REQUIRED_FIELD)

        # Mirrors your C++ logic: you *looked for* browserLaunchOptions under `solution`,
        # even though ToJson writes it at the root. I'm keeping that behavior faithful.
        launch_options = BrowserLaunchOptions()
        raw_launch_options = raw.get("browserLaunchOptions")
        if isinstance(raw_launch_options, dict):
            launch_options = BrowserLaunchOptions.from_json(raw_launch_options)

        solution = StudioSolution(
            solution_name=str(raw_solution["solutionName"]),
            solution_directory=".",
            create_directory_for_solution=bool(raw_solution["solutionDirectoryCreated"]),
            base_url=str(raw_solution["baseUrl"]),
            selected_browser=str(raw_solution["browser"]),
            launch_browser_automatically=bool(raw_solution["launchBrowserAutomatically"]),
            browser_launch_options=launch_options,
            default_screenshots_policy=default_screenshots_policy
        )

        return SolutionLoadResult(solution, SolutionLoadError.NONE_)

    def get_solution_directory(self) -> Path:
        """
        Compute the root directory of this solution on disk.

        Returns:
            The resolved solution directory path.
        """
        base = Path(self.solution_directory)
        return base / self.solution_name \
            if self.create_directory_for_solution else base

    def get_solution_file_path(self) -> Path:
        """
        Get the full path to the solution file (.wws).

        Returns:
            Path to the solution file.
        """
        return self.get_solution_directory() / f"{self.solution_name}.wws"

    def get_pages_directory(self) -> Path:
        """
        Get the Pages directory path.

        Returns:
            Path to the Pages directory.
        """
        return self.get_solution_directory() / PAGES_DIRECTORY

    def get_scripts_directory(self) -> Path:
        """
        Get the Scripts directory path.

        Returns:
            Path to the Scripts directory.
        """
        return self.get_solution_directory() / SCRIPTS_DIRECTORY

    def get_recordings_directory(self) -> Path:
        """
        Get the Recordings directory path.

        Returns:
            Path to the Recordings directory.
        """
        return self.get_solution_directory() / RECORDINGS_DIRECTORY

    def get_test_suites_directory(self) -> Path:
        """
        Get the Test Suites directory path.

        Returns:
            Path to the Test Suites directory.
        """
        return self.get_solution_directory() / TEST_SUITES_DIRECTORY

    def ensure_directory_structure(self) -> SolutionDirectoryCreateStatus:
        """
        Ensure all required directories for this solution exist.

        Returns:
            A SolutionDirectoryCreateStatus describing success or failure.
        """
        try:
            self.get_solution_directory().mkdir(parents=True, exist_ok=True)
        except OSError:
            return SolutionDirectoryCreateStatus.CANNOT_CREATE_ROOT

        try:
            self.get_pages_directory().mkdir(parents=True, exist_ok=True)
        except OSError:
            return SolutionDirectoryCreateStatus.CANNOT_CREATE_PAGES

        try:
            self.get_scripts_directory().mkdir(parents=True, exist_ok=True)
        except OSError:
            return SolutionDirectoryCreateStatus.CANNOT_CREATE_SCRIPTS

        try:
            self.get_recordings_directory().mkdir(parents=True, exist_ok=True)
        except OSError:
            return SolutionDirectoryCreateStatus.CANNOT_CREATE_RECORDINGS

        try:
            self.get_test_suites_directory().mkdir(parents=True, exist_ok=True)
        except OSError:
            return SolutionDirectoryCreateStatus.CANNOT_CREATE_TEST_SUITES

        return SolutionDirectoryCreateStatus.NONE_

    def discover_recording_files(self) -> None:
        """
        Scan the Recordings directory for valid recording metadata files.

        Returns:
            A list of successfully loaded RecordingMetadata objects.
        """
        recordings: typing.List["RecordingMetadata"] = []
        rec_dir = self.get_recordings_directory()

        if not rec_dir.exists():
            return

        for entry in rec_dir.iterdir():
            if not entry.is_file():
                continue
            if entry.suffix != ".wwrec":
                continue

            result = RecordingMetadata.from_file(entry)

            if not result.recording:
                wx.LogWarning(
                    f"Skipping recording {entry}:\n"
                    f"{recording_load_error_to_str(result.error)}"
                )
                continue

            recordings.append(result.recording)

        # Build recordings cache
        self.recordings_cache = {rec.id: rec for rec in recordings}

    def generate_next_recording_name(self) -> str:
        """
        Generate a unique sequential recording name.

        Returns:
            A recording name of the form 'Recording N'.
        """
        recordings = self.get_all_recordings()

        max_index: int = 0
        prefix: str = "Recording "

        for rec in recordings:
            name = getattr(rec, "name", "")
            if len(name) <= len(prefix):
                continue

            # NOTE: Not sure we should do this - investigate!!
            if not name.startswith(prefix):
                continue

            try:
                value = int(name[len(prefix):])
                max_index = max(max_index, value)

            # Ignore malformed names
            except ValueError:
                pass

        return f"Recording {max_index + 1}"

    def open_recording(self, metadata: RecordingMetadata) -> RecordingViewContext:
        """
        Open a recording for viewing.

        Args:
            metadata:
                Recording metadata to open.

        Returns:
            A RecordingViewContext instance.
        """
        recording_file = Path(metadata.file_path).resolve()
        ctx = RecordingViewContext(metadata, recording_file)
        return ctx

    def get_recording_by_id(self, recording_id):
        """Retrieve a recording by its unique identifier.

        Args:
            recording_id (str): The unique identifier of the recording.

        Returns:
            Recording | None: The matching recording object if found, otherwise None.
        """
        return self.recordings_cache.get(recording_id)

    def get_all_recordings(self):
        """Retrieve all cached recordings.

        Returns:
            list[Recording]: A list of all recording objects stored in the cache.
        """
        return list(self.recordings_cache.values())


def solution_load_error_to_str(error_enum: SolutionLoadError) -> str:
    """
    Convert a SolutionLoadError to a user-facing message.

    Args:
        error_enum:
            The error enum value.

    Returns:
        A human-readable error description.
    """
    if error_enum == SolutionLoadError.FILE_MALFORMED:
        return "The solution file is malformed or corrupted."

    if error_enum == SolutionLoadError.MISSING_VERSION:
        return "The solution file does not specify a version."

    if error_enum == SolutionLoadError.UNSUPPORTED_VERSION:
        return "This solution file was created with a newer WebWeaver version"

    if error_enum == SolutionLoadError.MISSING_SOLUTION_OBJECT:
        return "The solution file is missing required data."

    if error_enum == SolutionLoadError.MISSING_REQUIRED_FIELD:
        return "The solution file is incomplete."

    return "Unknown solution load error."


def solution_directory_error_to_str(
        error_enum: SolutionDirectoryCreateStatus) -> str:
    """
    Convert a directory creation error to a user-facing message.

    Args:
        error_enum:
            The directory creation status.

    Returns:
        A human-readable error description.
    """
    if error_enum == SolutionDirectoryCreateStatus.CANNOT_CREATE_ROOT:
        return "Unable to create the solution directory."

    if error_enum == SolutionDirectoryCreateStatus.CANNOT_CREATE_PAGES:
        return "Unable to create the Pages folder."

    if error_enum == SolutionDirectoryCreateStatus.CANNOT_CREATE_SCRIPTS:
        return "Unable to create the Scripts folder."

    if error_enum == SolutionDirectoryCreateStatus.CANNOT_CREATE_RECORDINGS:
        return "Unable to create the Recordings folder."

    return "Unknown error"
