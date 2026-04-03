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
from dataclasses import dataclass
from logging import Logger
import threading
import time
import typing
import wx
from webweaver.studio.browsing.studio_browser import StudioBrowser
from webweaver.studio.playback.playback_engine import PlaybackEngine
from webweaver.studio.recording.recording import Recording


@dataclass
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
    on_step_started: typing.Callable[[int], None] = None
    on_step_passed: typing.Callable[[int], None] = None
    on_step_failed: typing.Callable[[int], None] = None
    on_playback_finished: typing.Callable[[int], None] = None


class RecordingPlaybackSession:
    """
    Executes a recorded WebWeaver recording step-by-step using a StudioBrowser.

    A RecordingPlaybackSession represents a single playback run over a
    Recording. It maintains an instruction pointer into the recording's event
    list and exposes a simple control surface for starting, stopping, and
    stepping through events one at a time.

    This class is intentionally stateful and UI-friendly: it is designed to be
    driven by toolbar actions such as Play, Step, Pause, and Stop, and to report
    failures immediately when an event cannot be executed.
    """
    # py____lint: ____disable____=too-many-instance-attributes

    def __init__(self,
                 browser: StudioBrowser,
                 recording: Recording,
                 logger: Logger):
        """
        Create a new playback session for the given recording.

        :param browser: StudioBrowser instance used to execute playback actions.
        :param recording: The Recording to be played back.
        :param logger: Base logger used for emitting playback diagnostics.
        """
        self._browser = browser
        self._recording = recording
        self._index = 0
        self._running = False
        self._logger = logger.getChild(__name__)
        self.callback_events = PlaybackCallbackEvents()
        self._thread = None
        self._engine: PlaybackEngine = PlaybackEngine(browser,
                                                      recording,
                                                      logger)

    def start(self):
        """
        Start playback from the beginning of the recording.

        This resets the internal instruction pointer to the first event and
        marks the session as running. No events are executed until step() is
        called.
        """

        # Check if playback is already running.
        if self._running:
            return

        if self._thread and self._thread.is_alive():
            self._logger.debug("Playback thread is still shutting down")
            return

        self._running = True
        self._index = 0
        self._engine.context.clear()

        self._engine.stop_event.clear()

        self._thread = threading.Thread(
            target=self._playback_loop,
            daemon=True
        )
        self._thread.start()

    def stop(self):
        """
        Stop playback.

        This halts the session and prevents any further events from being
        executed until start() is called again.
        """
        self._running = False
        self._engine.stop_event.set()

    def step(self) -> bool:
        """
        Execute the next event in the recording.

        This method executes exactly one recorded event and advances the
        internal instruction pointer if the event succeeds.

        If playback is not currently running, or if the end of the recording
        has been reached, this method returns False and performs no action.

        If the event fails, playback is stopped and False is returned.

        :return: True if an event was executed successfully, False otherwise.
        """
        if not self._running:
            return False

        if self._index >= len(self._recording.events):
            self.stop()
            return False

        current_index = self._index

        if self.callback_events.on_step_started:
            wx.CallAfter(self.callback_events.on_step_started, current_index)

        event = self._recording.events[current_index]
        result = self._engine.execute_event(event)

        if not result.ok:
            if self.callback_events.on_step_failed:
                wx.CallAfter(self.callback_events.on_step_failed,
                             current_index,
                             result.error)

            self.stop()
            return False

        # success
        if self.callback_events.on_step_passed:
            wx.CallAfter(self.callback_events.on_step_passed, current_index)

        self._index += 1

        return True

    def _playback_loop(self):
        try:
            while self._running and not self._engine.stop_event.is_set():
                still_running = self.step()

                if not still_running:
                    break

                time.sleep(0.001)

        finally:
            self._running = False
            self._thread = None

            if self.callback_events.on_playback_finished:
                wx.CallAfter(self.callback_events.on_playback_finished)

