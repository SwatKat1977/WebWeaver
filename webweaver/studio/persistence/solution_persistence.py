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
import enum
import json
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from webweaver.studio.studio_solution import StudioSolutions


class SolutionSaveStatus(enum.Enum):
    """
    Enumeration of possible outcomes when saving a StudioSolution to disk.

    Each value represents either a successful save or a specific category of failure
    that can occur during the persistence process.
    """
    OK = "Ok"
    DIR_CREATE_FAILED = "Solution directory structure creation failed"
    CANNOT_WRITE_SOLUTION_FILE = "Cannot write Solution File"


class SolutionDirectoryCreateStatus(enum.Enum):
    """
    Enumeration of possible outcomes when creating a solution's directory structure.

    This enum is used to precisely describe which stage of directory creation failed,
    allowing the caller to present accurate diagnostics or recovery options.
    """
    NONE_ = 0
    CANNOT_CREATE_ROOT = enum.auto()
    CANNOT_CREATE_PAGES = enum.auto()
    CANNOT_CREATE_SCRIPTS = enum.auto()
    CANNOT_CREATE_RECORDINGS = enum.auto()


class SolutionPersistence:
    """
    Handles loading and saving StudioSolution instances to and from disk.

    This class defines the persistence boundary for solution data and is responsible for:

    - Creating and validating the on-disk directory structure for a solution
    - Serialising StudioSolution objects to JSON files
    - Deserialising StudioSolution objects from JSON files

    All file system and I/O concerns related to solution persistence are intentionally
    isolated in this class to keep the rest of the application free from low-level
    storage logic.
    """

    @staticmethod
    def ensure_directory_structure(solution:  "StudioSolution") \
            -> SolutionDirectoryCreateStatus:
        """
        Ensure all required directories for this solution exist.

        Returns:
            A SolutionDirectoryCreateStatus describing success or failure.
        """
        try:
            solution.get_solution_directory().mkdir(parents=True,
                                                    exist_ok=True)
        except OSError:
            return SolutionDirectoryCreateStatus.CANNOT_CREATE_ROOT

        try:
            solution.get_pages_directory().mkdir(parents=True, exist_ok=True)
        except OSError:
            return SolutionDirectoryCreateStatus.CANNOT_CREATE_PAGES

        try:
            solution.get_scripts_directory().mkdir(parents=True, exist_ok=True)
        except OSError:
            return SolutionDirectoryCreateStatus.CANNOT_CREATE_SCRIPTS

        try:
            solution.get_recordings_directory().mkdir(parents=True,
                                                      exist_ok=True)
        except OSError:
            return SolutionDirectoryCreateStatus.CANNOT_CREATE_RECORDINGS

        return SolutionDirectoryCreateStatus.NONE_

    @staticmethod
    def save_to_disk(solution:  "StudioSolution") -> SolutionSaveStatus:
        """
        Save a StudioSolution to disk.

        This method:

        - Ensures the solution's directory structure exists
        - Serialises the solution to JSON
        - Writes the solution file to disk

        If any step fails, an appropriate SolutionSaveStatus is returned to allow the
        caller to present a meaningful error message to the user.

        :param solution: The solution to save.
        :return: A SolutionSaveStatus indicating success or the type of failure.
        """
        # Ensure solution + subdirectories exist
        if SolutionPersistence.ensure_directory_structure(solution) != \
                SolutionDirectoryCreateStatus.NONE_:
            return SolutionSaveStatus.DIR_CREATE_FAILED

        solution_file = solution.get_solution_file_path()

        # Serialize to JSON
        data = solution.to_json()

        try:
            with open(solution_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
            return SolutionSaveStatus.OK

        except OSError:
            return SolutionSaveStatus.CANNOT_WRITE_SOLUTION_FILE

    @staticmethod
    def load_from_disk(solution_file: Path) ->  dict:
        """
        Load a StudioSolution from disk.

        This method reads the specified solution file, parses the JSON content, and
        constructs a StudioSolution instance from it.

        :param solution_file: Path to the solution file to load.
        :return: A fully constructed StudioSolution instance.
        :raises OSError: If the file cannot be read.
        :raises json.JSONDecodeError: If the file does not contain valid JSON.
        :raises ValueError: If the file content is not a valid solution format.
        """
        with solution_file.open("r", encoding="utf-8") as f:
            return json.load(f)
