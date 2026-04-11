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
import logging
import wx
from webweaver.studio.browsing.studio_browser import StudioBrowser
from webweaver.studio.playback.playback_session_base import \
    PlaybackCallbackEvents
from webweaver.studio.playback.recording_playback_session import \
    RecordingPlaybackSession
from webweaver.studio.studio_solution import StudioSolution
from webweaver.studio.test_suites.test_suite import TestSuite


class TestSuitePlaybackSession:
    """Coordinate playback of a test suite composed of multiple recordings.

    This class manages the sequential execution of multiple
    ``RecordingPlaybackSession`` instances. It acts as a higher-level
    orchestrator, translating recording-level step callbacks into
    suite-level callbacks that include both recording and step context.

    Playback proceeds recording-by-recording. If any step fails, the
    entire suite playback is stopped immediately.

    Args:
        browser: The browser instance used for playback execution.
        suite: The test suite containing recordings to be executed.
            Expected to have a ``recordings`` iterable.
        logger: A logger instance used for logging. A child logger scoped
            to this class will be created.

    Attributes:
        callback_events (PlaybackCallbackEvents): Public callback interface
            for receiving playback events. Callbacks are invoked via
            ``wx.CallAfter`` to ensure thread-safe UI updates.

    Notes:
        - Recording playback is strictly sequential (no parallel execution).
        - A failure in any step halts the entire suite.
        - A step index of ``-1`` is used to signal the start of a recording.
    """

    def __init__(self,
                 browser: StudioBrowser,
                 suite: TestSuite,
                 solution: StudioSolution,
                 logger: logging.Logger):
        """Initialise the TestSuitePlaybackSession.

        Args:
            browser: The browser instance used for playback execution.
            suite: The test suite containing recordings.
            logger: A logger instance.
        """
        self._browser: StudioBrowser = browser
        self._suite: TestSuite = suite
        self._logger: logging.Logger = logger.getChild(self.__class__.__name__)
        self._solution = solution

        self._index: int = 0  # current recording index
        self._running: bool = False
        self._current_session: RecordingPlaybackSession | None = None

        # Public callback interface
        self.callback_events = PlaybackCallbackEvents()

    def start(self):
        """Start playback of the test suite.

        Begins execution from the first recording in the suite. If playback
        is already running, this method does nothing.
        """
        if self._running:
            return

        self._running = True
        self._index = 0

        self._start_next_recording()

    def stop(self):
        """Stop playback of the test suite.

        Stops the current recording (if any) and prevents further recordings
        from being executed.
        """
        self._running = False

        if self._current_session:
            self._current_session.stop()
            self._current_session = None

    def _start_next_recording(self):
        """Start playback of the next recording in the suite.

        If all recordings have been processed, finalizes playback.
        """
        if not self._running:
            return

        if self._index >= len(self._suite.recordings):
            self._finish()
            return

        recording = self._suite.recordings[self._index]

        # Notify recording started
        if self.callback_events.on_step_started:
            wx.CallAfter(self.callback_events.on_step_started,
                         self._index, -1)  # -1 = recording start marker

        self._current_session = RecordingPlaybackSession(self._browser,
                                                         recording,
                                                         self._logger,
                                                         self._solution)

        self._bind_recording_callbacks(self._current_session)

        self._current_session.start()

    def _bind_recording_callbacks(self, session: RecordingPlaybackSession):
        """Bind and wrap recording-level callbacks.

        Translates callbacks from a ``RecordingPlaybackSession`` into
        suite-level callbacks by injecting the current recording index.

        Args:
            session (RecordingPlaybackSession): The recording playback
                session whose callbacks will be wrapped.
        """

        session.callback_events.on_step_started = self._on_step_started
        session.callback_events.on_step_passed = self._on_step_passed
        session.callback_events.on_step_failed = self._on_step_failed
        session.callback_events.on_playback_finished = \
            self._on_recording_finished

    def _on_step_started(self, step_index: int):
        """Handle a step start event from the current recording.

        Args:
            step_index (int): Index of the step within the recording.
        """
        if self.callback_events.on_step_started:
            wx.CallAfter(self.callback_events.on_step_started,
                         self._index,
                         step_index)

    def _on_step_passed(self, step_index: int):
        """Handle a successful step completion.

        Args:
            step_index (int): Index of the step within the recording.
        """
        if self.callback_events.on_step_passed:
            wx.CallAfter(self.callback_events.on_step_passed,
                         self._index,
                         step_index)

    def _on_step_failed(self, step_index: int, reason: str):
        """Handle a failed step and stop suite playback.

        Args:
            step_index (int): Index of the failed step.
            reason (str): Description of the failure.
        """
        if self.callback_events.on_step_failed:
            wx.CallAfter(self.callback_events.on_step_failed,
                         self._index,
                         step_index,
                         reason)

        # Stop entire suite on failure
        self.stop()

    def _on_recording_finished(self):
        """Handle completion of the current recording.

        Advances to the next recording if playback is still active.
        """
        if not self._running:
            return

        self._index += 1
        self._start_next_recording()

    def _finish(self):
        """Finalize suite playback.

        Marks playback as complete and triggers the finished callback.
        """
        self._running = False
        self._current_session = None

        if self.callback_events.on_playback_finished:
            wx.CallAfter(self.callback_events.on_playback_finished)
