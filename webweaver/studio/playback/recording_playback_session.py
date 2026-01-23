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
from browsing.studio_browser import PlaybackStepResult, StudioBrowser
from recording.recording import Recording


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

    def __init__(self,
                 browser: StudioBrowser,
                 recording: Recording,
                 logger: Logger):
        self._browser = browser
        self._recording = recording
        self._index = 0
        self._running = False
        self._logger = logger.getChild(__name__)
        """
        Create a new playback session for the given recording.

        :param browser: StudioBrowser instance used to execute playback actions.
        :param recording: The Recording to be played back.
        :param logger: Base logger used for emitting playback diagnostics.
        """

    def start(self):
        """
        Start playback from the beginning of the recording.

        This resets the internal instruction pointer to the first event and
        marks the session as running. No events are executed until step() is
        called.
        """
        self._running = True
        self._index = 0

    def stop(self):
        """
        Stop playback.

        This halts the session and prevents any further events from being
        executed until start() is called again.
        """
        self._running = False

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

        event = self._recording.events[self._index]
        result = self._execute_event(event)

        if not result.ok:
            print("Playback failed:", result.error)
            self.stop()
            return False

        self._index += 1

        return True

    def _execute_event(self, event: dict):
        """
        Execute a single recorded event.

        This method dispatches the event to the appropriate playback handler
        on the StudioBrowser based on the event's type field.

        Unknown or unsupported event types are ignored and treated as successful
        no-ops.

        :param event: The recorded event dictionary.
        :return: A PlaybackStepResult indicating success or failure of the event.
        """
        event_type = event.get("type")
        payload = event.get("payload", {})

        if event_type == "dom.check":
            self._logger.debug("[PLAYBACK EVENT] Check: %s", payload)
            return self._browser.playback_check(payload)

        if event_type == "dom.click":
            self._logger.debug("[PLAYBACK EVENT] Button: %s", payload)
            return self._browser.playback_click(payload)

        if event_type == "nav.goto":
            self._browser.open_page(event["url"])

        if event_type == "dom.select":
            self._logger.debug("[PLAYBACK EVENT] Dropdown: %s", payload)
            return self._browser.playback_select(payload)

        if event_type == "dom.type":
            self._logger.debug("[PLAYBACK EVENT] Text: %s", payload)
            return self._browser.playback_type(payload)

        self._logger.debug("[PLAYBACK EVENT] Unknown event: %s",
                           event_type)

        return PlaybackStepResult(ok=True, error="")
