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
import enum
from typing import Callable, Optional

class StudioState(enum.Enum):
    """
    Represents the high-level state of the Studio application.
    """
    NO_SOLUTION = enum.auto()
    SOLUTION_LOADED = enum.auto()
    RECORDING_RUNNING = enum.auto()
    RECORDING_PAUSED = enum.auto()
    INSPECTING = enum.auto()

StateChangedCallback = Callable[[StudioState], None]

class StudioStateController:
    """
    Central coordinator for studio state transitions.

    The StudioStateController encapsulates the current high-level state of the
    studio and provides a controlled API for transitioning between states in
    response to user intent (e.g. loading a solution, starting or pausing a
    recording, toggling the inspector).

    State changes are gated by UI readiness: transitions may occur at any time,
    but notifications are only emitted once the UI has declared itself ready.
    This prevents premature updates during application startup or teardown.

    This class is a direct Python analogue of the C++ StudioStateController and
    is intentionally UI-agnostic. It does not perform any UI actions itself;
    instead, it notifies interested listeners via an optional callback when the
    effective studio state changes.

    Parameters
    ----------
    on_state_changed : Optional[StateChangedCallback]
        Optional callback invoked when the studio state changes and the UI is
        ready. The callback is passed the new StudioState value.
    """

    def __init__(self, on_state_changed: Optional[StateChangedCallback] = None):
        self._state: StudioState = StudioState.NO_SOLUTION
        self._on_state_changed: Optional[StateChangedCallback] = \
            on_state_changed
        self._ui_ready: bool = False

    @property
    def state(self) -> StudioState:
        """
        Get the current studio state.

        Returns
        -------
        StudioState
            The current state.
        """
        return self._state

    @property
    def ui_ready(self) -> bool:
        """
        Get whether the UI is ready to receive state change notifications.
        """
        return self._ui_ready

    @ui_ready.setter
    def ui_ready(self, ready: bool) -> None:
        """
        Set whether the UI is ready to receive state change notifications.
        """
        self._ui_ready = ready

    # User intents

    def on_solution_loaded(self) -> None:
        """
        Notify the controller that a solution has been successfully loaded.

        Transitions the studio into the SOLUTION_LOADED state.
        """
        self._set_state(StudioState.SOLUTION_LOADED)

    def on_solution_closed(self) -> None:
        """
        Notify the controller that the active solution has been closed.

        Resets the studio to the NO_SOLUTION state.
        """
        self._set_state(StudioState.NO_SOLUTION)

    def on_record_start_stop(self) -> None:
        """
        Handle the user's intent to start or stop recording.

        If a recording is currently running or paused, recording is stopped and
        the studio returns to the SOLUTION_LOADED state.

        If no recording is active, recording is started and the studio enters the
        RECORDING_RUNNING state.
        """
        if self._state in (StudioState.RECORDING_RUNNING,
                           StudioState.RECORDING_PAUSED):
            self._set_state(StudioState.SOLUTION_LOADED)

        elif self._state == StudioState.SOLUTION_LOADED:
            self._set_state(StudioState.RECORDING_RUNNING)

    def on_record_pause(self) -> None:
        """
        Toggle the paused state of an active recording.

        If recording is running, it is paused.
        If recording is paused, it is resumed.
        """
        if self._state == StudioState.RECORDING_RUNNING:
            self._set_state(StudioState.RECORDING_PAUSED)

        elif self._state == StudioState.RECORDING_PAUSED:
            self._set_state(StudioState.RECORDING_RUNNING)

    def on_inspector_toggle(self, shown: bool ) -> None:
        """
        Notify the controller that the inspector panel has been shown or hidden.

        When the inspector is shown, the studio enters the INSPECTING state.
        When the inspector is hidden, the studio returns to the SOLUTION_LOADED
        state.
        """
        if shown:
            self._set_state(StudioState.INSPECTING)

        else:
            self._set_state(StudioState.SOLUTION_LOADED)

    def _set_state(self, new_state: StudioState) -> None:
        """
        Internal state transition handler.

        Updates the current state and notifies listeners if the UI is ready.
        """
        if self._state == new_state:
            return

        self._state = new_state

        # Don't notify until UI is ready
        if not self._ui_ready:
            return

        if self._on_state_changed:
            self._on_state_changed(self._state)
