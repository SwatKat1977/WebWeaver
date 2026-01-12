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
from studio_solution import StudioSolution


class SolutionDirectoryCreateStatus(enum.Enum):
    """
    Enumerates possible failures when creating a solution's directory structure.
    """
    NONE_ = 0
    CANNOT_CREATE_ROOT = enum.auto()
    CANNOT_CREATE_PAGES = enum.auto()
    CANNOT_CREATE_SCRIPTS = enum.auto()
    CANNOT_CREATE_RECORDINGS = enum.auto()


class SolutionPersistence:

    @staticmethod
    def ensure_directory_structure(solution: StudioSolution) \
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
    def save_disk(solution: StudioSolution) -> bool:
        # Ensure solution + subdirectories exist
        if SolutionPersistence.ensure_directory_structure(solution) != \
                SolutionDirectoryCreateStatus.NONE_:
            return False

        solution_file = solution.get_solution_file_path()

        # Serialize to JSON
        data = solution.to_json()

        try:
            with open(solution_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
            return True
        except OSError:
            return False
