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
from logging import Logger
from webweaver.studio.browsing.studio_browser import StudioBrowser
from webweaver.studio.playback.playback_engine import PlaybackEngine
from webweaver.studio.playback.playback_session_base import PlaybackSessionBase
from webweaver.studio.recording.recording import Recording
from webweaver.studio.studio_solution import StudioSolution


class RecordingPlaybackSession(PlaybackSessionBase):
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

    def __init__(self,
                 browser: StudioBrowser,
                 recording: Recording,
                 logger: Logger,
                 solution: StudioSolution):
        super().__init__(logger, solution, recording, browser)
        self._browser = browser
        self._engine: PlaybackEngine = PlaybackEngine(browser,
                                                      recording,
                                                      logger)

    def _get_step_count(self) -> int:
        return len(self._recording.events)

    def _execute_step(self, index: int):
        event = self._recording.events[index]
        return self._engine.execute_event(event)

    def _on_stop(self):
        self._engine.stop_event.set()
