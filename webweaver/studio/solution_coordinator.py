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
import json
import logging
from pathlib import Path
from typing import Optional
from webweaver.studio.persistence.solution_persistence import (
    SolutionPersistence,
    SolutionSaveStatus,
    SolutionDirectoryCreateStatus)
from webweaver.studio.recent_solutions_manager import RecentSolutionsManager
from webweaver.studio.recording.recording_session import RecordingSession
from webweaver.studio.studio_solution import (
    StudioSolution,
    solution_load_error_to_str)
from webweaver.studio.ui.solution_create_wizard.solution_create_wizard_data import \
    SolutionCreateWizardData


class SolutionCoordinator:
    """
    Owns the lifecycle of the active solution, its recording session, and
    the recent-solutions list.

    All file I/O and domain-level validation is handled here. The coordinator
    returns plain (ok, error_message) tuples — UI dialogs and panel refreshes
    are the caller's responsibility.
    """

    def __init__(self, logger: logging.Logger) -> None:
        self._logger = logger
        self._current_solution: Optional[StudioSolution] = None
        self._recording_session: Optional[RecordingSession] = None
        self._recent_solutions: RecentSolutionsManager = RecentSolutionsManager()
        self._recent_solutions.load()

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def current_solution(self) -> Optional[StudioSolution]:
        """The currently loaded solution, or None."""
        return self._current_solution

    @property
    def recording_session(self) -> Optional[RecordingSession]:
        """The recording session bound to the current solution, or None."""
        return self._recording_session

    @property
    def recent_solutions(self) -> RecentSolutionsManager:
        """The recent-solutions manager."""
        return self._recent_solutions

    # ------------------------------------------------------------------
    # Operations
    # ------------------------------------------------------------------

    def create(self, data: SolutionCreateWizardData) -> tuple[bool, str]:
        """Create and persist a new solution from wizard data.

        On success, ``current_solution`` and ``recording_session`` are set and
        the solution is added to the recent-solutions list.

        Returns:
            ``(True, "")`` on success, or ``(False, error_message)`` on failure.
        """
        solution = StudioSolution(
            data.solution_name,
            data.solution_directory,
            data.create_solution_dir,
            data.base_url,
            data.browser,
            data.launch_browser_automatically,
            data.browser_launch_options)

        status = SolutionPersistence.save_to_disk(solution)
        if status is not SolutionSaveStatus.OK:
            return False, status.value

        self._current_solution = solution
        self._recording_session = RecordingSession(solution)
        self._recent_solutions.add_solution(solution.get_solution_file_path())

        return True, ""

    def open(self, solution_file: Path) -> tuple[bool, str]:
        """Load a solution from disk.

        On success, ``current_solution`` and ``recording_session`` are set and
        the solution is added to the recent-solutions list.  The caller should
        check ``current_solution.launch_browser_automatically`` to decide
        whether to launch the browser.

        Returns:
            ``(True, "")`` on success, or ``(False, error_message)`` on failure.
        """
        if not solution_file.exists():
            return False, "Solution file does not exist."

        try:
            raw_data = SolutionPersistence.load_from_disk(solution_file)
            result = StudioSolution.from_json(raw_data)
        except (OSError, json.JSONDecodeError) as exc:
            return False, f"Failed to read solution file:\n{exc}"

        if result.solution is None:
            return False, solution_load_error_to_str(result.error)

        solution = result.solution
        solution.solution_directory = str(solution_file.resolve().parent)
        solution.create_directory_for_solution = False

        status = solution.ensure_directory_structure()
        if status != SolutionDirectoryCreateStatus.NONE_:
            self._logger.error("Failed to prepare solution folders: %s", status)
            return False, "Failed to prepare solution folders."

        self._current_solution = solution
        self._recording_session = RecordingSession(solution)
        self._recent_solutions.add_solution(solution_file)

        return True, ""

    def close(self) -> None:
        """Tear down the current solution and its recording session.

        If a recording is active it is stopped and flushed to disk before the
        session is discarded.  Safe to call when no solution is loaded.
        """
        if self._recording_session and self._recording_session.is_recording():
            self._recording_session.stop()
        self._recording_session = None
        self._current_solution = None

    def save_current(self) -> tuple[bool, str]:
        """Persist the current solution's settings to disk.

        Returns:
            ``(True, "")`` on success, or ``(False, error_message)`` on failure.
        """
        if not self._current_solution:
            return False, "No solution is loaded."

        status = SolutionPersistence.save_to_disk(self._current_solution)
        if status is not SolutionSaveStatus.OK:
            return False, status.value
        return True, ""
