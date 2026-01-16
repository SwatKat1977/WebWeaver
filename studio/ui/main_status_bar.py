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
from typing import Optional
import wx


class StatusBarElement(enum.Enum):
    """
    Enumeration of status bar field indices.

    This enum defines the logical layout of the main application status bar.
    Each value corresponds to a fixed field index in the wx status bar and
    should be used instead of hard-coded integers when updating status text.

    Fields:

        STATUS_MESSAGE (0):
            General-purpose status messages (e.g. "Ready", progress updates,
            or short-lived operation feedback).

        SOLUTION_NAME (1):
            Displays the name of the currently loaded solution, or indicates
            that no solution is loaded.

        CURRENT_MODE (2):
            Shows the current application mode and recording state
            (e.g. "Mode: Editing", "Mode: Recording ●").

        SAVE_STATUS (3):
            Indicates whether there are unsaved changes or whether all changes
            are safely saved.

        BROWSER_STATUS (4):
            Indicates whether the controlled browser instance is currently
            running or stopped.
    """
    STATUS_MESSAGE = 0
    SOLUTION_NAME = 1
    CURRENT_MODE = 2
    SAVE_STATUS = 3
    BROWSER_STATUS = 4


class MainStatusBar:
    """
    High-level facade for the application's main status bar.

    This class encapsulates creation and management of the wx.StatusBar owned
    by the main application frame and exposes a small, intention-revealing API
    for updating its fields.

    The status bar is divided into five fields that provide always-visible,
    high-level information about the current state of WebWeaver Studio:

        0. General status messages (e.g. "Ready", operation feedback)
        1. Currently loaded solution name
        2. Current mode and recording state (e.g. "Mode: Editing",
           "● Recording")
        3. Save state / dirty flag (e.g. "All changes saved",
           "Unsaved changes")
        4. Browser state (e.g. "Browser: Running", "Browser: Stopped")

    This object intentionally hides the underlying wx.StatusBar API and instead
    provides semantic methods such as `set_status_bar_mode()` or
    `set_status_bar_browser_running()`, so the rest of the application does not
    need to know how the status bar is structured internally.

    The wx.Frame passed to the constructor remains the owner of the actual
    wx.StatusBar; this class acts purely as a controller/facade.
    """
    def __init__(self, frame: wx.Frame):
        """
        Create and initialize the main application status bar.

        The status bar is divided into five fields that provide high-level,
        always-visible information about the current state of WebWeaver Studio:

            0. General status messages (e.g. "Ready", operation feedback)
            1. Currently loaded solution name
            2. Current mode and recording state (e.g. "Mode: Editing",
               "● Recording")
            3. Save state / dirty flag (e.g. "All changes saved", "Unsaved
               changes")
            4. Browser state (e.g. "Browser: Running", "Browser: Stopped")

        Each field is given a relative width so that more important contextual
        information (such as the solution name) has more space.
        """
        self._status_bar = frame.CreateStatusBar(5)

        # Relative widths
        self._status_bar.SetStatusWidths([
            -2,  # General
            -3,  # Solution
            -2,  # Mode / Recording
            -1,  # Save state
            -1,  # Browser
        ])

        # Initial values
        self._status_bar.SetStatusText(
            "Ready", StatusBarElement.STATUS_MESSAGE.value)
        self._status_bar.SetStatusText("No solution loaded",
                                       StatusBarElement.SOLUTION_NAME.value)
        self._status_bar.SetStatusText("Mode: Editing",
                                       StatusBarElement.CURRENT_MODE.value)
        self._status_bar.SetStatusText("All changes saved",
                                       StatusBarElement.SAVE_STATUS.value)
        self._status_bar.SetStatusText("Browser: Stopped",
                                       StatusBarElement.BROWSER_STATUS.value)

    def set_status_bar_status_message(self, msg: str):
        """
        Set the general-purpose status message in the status bar.

        This field is intended for short-lived feedback such as "Ready",
        progress updates, or the result of user actions.

        :param msg: The message text to display.
        """
        self._status_bar.SetStatusText(msg,
                                       StatusBarElement.STATUS_MESSAGE.value)

    def set_status_bar_current_solution(self, solution_name: Optional[str]):
        """
        Update the status bar to reflect the currently loaded solution.

        If no solution name is provided, the status bar will indicate that
        no solution is currently loaded.

        :param solution_name: The solution file name, or None if no solution
                              is loaded.
        """
        if not solution_name:
            self._status_bar.SetStatusText("No solution loaded",
                                           StatusBarElement.SOLUTION_NAME.value)
        else:
            self._status_bar.SetStatusText(f"Solution: {solution_name}",
                                           StatusBarElement.SOLUTION_NAME.value)

    def set_status_bar_mode(self, mode_name: str, is_recording: bool):
        """
        Update the status bar to show the current application mode and
        recording state.

        When recording is active, a recording indicator is appended to the
        mode text.

        :param mode_name: Human-readable name of the current mode
                          (e.g. "Editing", "Recording", "Playback").
        :param is_recording: True if a recording session is currently active.
        """
        text = f"Mode: {mode_name}"
        if is_recording:
            text += "  ● Recording"
        self._status_bar.SetStatusText(text,
                                       StatusBarElement.CURRENT_MODE.value)

    def set_status_bar_dirty(self, is_dirty: bool):
        """
        Update the status bar to reflect whether there are unsaved changes.

        :param is_dirty: True if the current solution has unsaved changes,
                         False if all changes are saved.
        """
        if is_dirty:
            self._status_bar.SetStatusText("Unsaved changes",
                                           StatusBarElement.SAVE_STATUS.value)
        else:
            self._status_bar.SetStatusText("All changes saved",
                                           StatusBarElement.SAVE_STATUS.value)

    def set_status_bar_browser_running(self, is_running: bool):
        """
        Update the status bar to reflect the current browser runtime state.

        :param is_running: True if the controlled browser instance is currently
                           running, False if it is stopped.
        """
        if is_running:
            self._status_bar.SetStatusText(
                "Browser: Running", StatusBarElement.BROWSER_STATUS.value)
        else:
            self._status_bar.SetStatusText(
                "Browser: Stopped", StatusBarElement.BROWSER_STATUS.value)
