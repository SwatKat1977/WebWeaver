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
import datetime
import logging
import threading
import time
import typing
from pathlib import Path
import wx
from webweaver.studio.browsing.studio_browser import StudioBrowser
from webweaver.studio.recording.recording import Recording
from webweaver.studio.studio_solution import StudioSolution, ScreenshotPolicy


class PlaybackCallbackEvents:
    """
    Container for optional playback lifecycle callbacks.

    This dataclass groups together a set of callback functions that can be
    provided by the UI or other controlling code to receive notifications
    about playback progress and results.

    All callbacks are optional. If a callback is None, it is simply not called.

    Callbacks:

    - on_step_started(index: int) -> None
        Called when playback begins executing a step.

    - on_step_passed(index: int) -> None
        Called when a step completes successfully.

    - on_step_failed(index: int, reason: str) -> None
        Called when a step fails. The reason string contains a human-readable
        error message describing the failure.

    - on_playback_finished() -> None
        Called once playback has finished, either because all steps completed
        or because playback stopped due to a failure.
    """
    # pylint: disable=too-few-public-methods
    on_step_started: typing.Callable[[int], None] = None
    on_step_passed: typing.Callable[[int], None] = None
    on_step_failed: typing.Callable[[int], None] = None
    on_playback_finished: typing.Callable[[int], None] = None


class PlaybackSessionBase:
    """Base class for managing step-based playback execution in a background thread.

    This class provides a threaded playback loop that iterates through a sequence
    of steps, executing them one at a time while emitting UI-safe callback events.
    Subclasses are expected to implement the step source and execution logic.

    Playback runs asynchronously on a daemon thread and can be controlled via
    `start()` and `stop()`. Each step is processed sequentially, and execution
    halts automatically on failure or when all steps are completed.

    Attributes:
        _index (int): The current step index being executed.
        _running (bool): Indicates whether playback is currently active.
        _thread (Optional[threading.Thread]): Background thread running playback.
        _logger (logging.Logger): Logger scoped to the subclass name.
        callback_events (PlaybackCallbackEvents): Container for playback callbacks.

    Callback Events:
        on_step_started (Callable[[int], None] | None):
            Invoked when a step begins execution. Receives the step index.

        on_step_passed (Callable[[int], None] | None):
            Invoked when a step completes successfully. Receives the step index.

        on_step_failed (Callable[[int, Exception], None] | None):
            Invoked when a step fails. Receives the step index and error.

        on_playback_finished (Callable[[], None] | None):
            Invoked when playback completes or is stopped.

    Threading:
        - Playback runs on a daemon thread.
        - UI callbacks are dispatched using `wx.CallAfter` to ensure they are
          executed on the main thread.

    Methods:
        start():
            Starts playback from the beginning if not already running.

        stop():
            Stops playback gracefully.

        step() -> bool:
            Executes a single step. Returns True if execution should continue,
            or False if playback should stop.

    Subclass Responsibilities:
        Subclasses must implement the following methods:

        _get_step_count() -> int:
            Returns the total number of steps available for playback.

        _execute_step(index: int):
            Executes a step at the given index and returns a result object
            with at least:
                - ok (bool): Whether the step succeeded.
                - error (Exception | Any): Error information if failed.
    """

    def __init__(self,
                 logger: logging.Logger,
                 solution: StudioSolution,
                 recording: Recording,
                 web_browser: StudioBrowser):
        """Initializes the playback session.

        Args:
            logger (logging.Logger): Base logger used to create a scoped logger
                for this playback session instance.
        """
        self._index = 0
        self._running = False
        self._thread = None
        self._logger = logger.getChild(self.__class__.__name__)
        self._solution: StudioSolution = solution
        self._recording: Recording = recording
        self.callback_events = PlaybackCallbackEvents()
        self._run_start_time: int = 0
        self._screenshots_dir: Path | None = None
        self._web_browser: StudioBrowser = web_browser

        # As recording-level screenshot policy fidelity isn't implemented, the
        # solution-level default policy will always be applied.
        self._screenshot_policy = self._solution.default_screenshots_policy

    def start(self):
        """Starts playback from the beginning.

        If playback is already running, this method does nothing. If a previous
        playback thread is still shutting down, startup is deferred.

        Creates and starts a daemon thread that runs the playback loop.
        """
        if self._running:
            return

        if self._thread and self._thread.is_alive():
            self._logger.debug("Playback thread still shutting down")
            return

        self._running = True
        self._index = 0
        self._run_start_time = int(time.time())

        if self._screenshot_policy != ScreenshotPolicy.OFF:
            base_dir: str = self._solution.screenshots_directory
            timestamp = datetime.datetime.fromtimestamp(
                self._run_start_time).strftime("%d-%m-%Y_%H-%M-%S")
            dir_name = f"run_{timestamp}"
            self._screenshots_dir = Path(base_dir) / dir_name

            if self._screenshots_dir.exists() and \
                    not self._screenshots_dir.is_dir():
                wx.MessageBox(
                    f"Screenshots directory '{self._screenshots_dir}' already "
                    "exists and is not a directory",
                    wx.ICON_INFORMATION)
                return

            try:
                self._screenshots_dir.mkdir(parents=True, exist_ok=True)

            except PermissionError:
                wx.MessageBox(
                    f"No write permissions for Screenshots "
                    f"directory '{self._screenshots_dir}'",
                    wx.ICON_INFORMATION)
                return

            except OSError as e:
                wx.MessageBox(
                    "Failed to create Screenshots directory "
                    f"'{self._screenshots_dir}'",
                    wx.ICON_INFORMATION)
                return

        self._thread = threading.Thread(
            target=self._playback_loop,
            daemon=True
        )
        self._thread.start()

    def stop(self):
        """Stops playback gracefully.

        Signals the playback loop to terminate. The background thread will exit
        naturally after the current step completes.
        """
        self._running = False
        self._on_stop()

    def step(self) -> bool:
        """Executes a single playback step.

        This method triggers the appropriate callbacks for step start, success,
        or failure. If a step fails or playback reaches the end, playback is stopped.

        Returns:
            bool: True if playback should continue, False otherwise.
        """
        if not self._running:
            return False

        if self._index >= self._get_step_count():
            self.stop()
            return False

        current_index = self._index

        if self.callback_events.on_step_started:
            wx.CallAfter(self.callback_events.on_step_started, current_index)

        result = self._execute_step(current_index)

        if not result.ok:
            if self.callback_events.on_step_failed:
                wx.CallAfter(self.callback_events.on_step_failed,
                             current_index,
                             result.error)

                if self._screenshot_policy in [ScreenshotPolicy.ALL_STEPS.value,
                                               ScreenshotPolicy.ON_FAILURE.value]:
                    self._perform_screenshot(current_index+1)

            self.stop()
            return False

        if self._screenshot_policy in [ScreenshotPolicy.ALL_STEPS.value]:
            self._perform_screenshot(current_index + 1)

        if self.callback_events.on_step_passed:
            wx.CallAfter(self.callback_events.on_step_passed, current_index)

        self._index += 1
        return True

    def _playback_loop(self):
        """Internal playback loop executed on a background thread.

        Continuously executes steps while playback is active. Ensures proper
        cleanup and emits a completion callback when playback finishes.
        """

        try:
            while self._running:
                if not self.step():
                    break
                time.sleep(0.001)
        finally:
            self._running = False
            self._thread = None

            if self.callback_events.on_playback_finished:
                wx.CallAfter(self.callback_events.on_playback_finished)

    # --- abstract hooks ---
    def _get_step_count(self) -> int:
        """Returns the total number of steps in the playback session.

        This method must be implemented by subclasses.

        Returns:
            int: Total number of steps.

        Raises:
            NotImplementedError: If not implemented by subclass.
        """
        raise NotImplementedError

    def _execute_step(self, index: int):
        """Executes a single step at the given index.

        This method must be implemented by subclasses.

        Args:
            index (int): Index of the step to execute.

        Returns:
            Any: A result object with at least:
                - ok (bool): Whether the step succeeded.
                - error (Any): Error information if the step failed.

        Raises:
            NotImplementedError: If not implemented by subclass.
        """
        raise NotImplementedError

    def _on_stop(self):
        """Optional override for subclasses"""

    def _perform_screenshot(self, step_index: int) -> None:
        """Capture a screenshot for the current step.

        Args:
            step_index (int): The index of the step being executed.
        """

        try:
            import os
            from datetime import datetime

            # File name: step_001.png etc.
            filename = (f"{self._recording.metadata.name}_"
                        f"step_{step_index:03d}.png")
            filepath = os.path.join(self._screenshots_dir, filename)

            self._web_browser.raw.save_screenshot(filepath)

        except Exception as e:
            # Never break playback because of screenshots
            print(f"[Screenshot Error] {e}")
