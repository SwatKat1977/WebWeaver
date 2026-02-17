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
import time
import typing
import selenium
from webweaver.studio.api_client import ApiClient
from webweaver.studio.browsing.studio_browser import (PlaybackStepResult,
                                                      StudioBrowser)
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
            if self.callback_events.on_playback_finished:
                self.callback_events.on_playback_finished()

            return False

        current_index = self._index

        if self.callback_events.on_step_started:
            self.callback_events.on_step_started(current_index)

        event = self._recording.events[current_index]
        result = self._execute_event(event)

        if not result.ok:
            if self.callback_events.on_step_failed:
                self.callback_events.on_step_failed(current_index,
                                                     result.error)

            self.stop()
            return False

        # success
        if self.callback_events.on_step_passed:
            self.callback_events.on_step_passed(current_index)

        self._index += 1

        return True

    def _execute_event(self, event: dict):
        """
        Execute a single recorded event and return a PlaybackStepResult.

        This method is crash-safe: any exception raised during execution is
        caught and converted into a PlaybackStepResult failure.
        """
        # pylint: disable=too-many-return-statements

        try:
            event_type = event.get("type")
            payload = event.get("payload", {})

            if event_type == "dom.check":
                self._logger.debug("[PLAYBACK EVENT] Check: %s", payload)
                return self._browser.playback_check(payload)

            if event_type == "dom.click":
                self._logger.debug("[PLAYBACK EVENT] Button: %s", payload)
                return self._browser.playback_click(payload)

            if event_type == "dom.select":
                self._logger.debug("[PLAYBACK EVENT] Dropdown: %s", payload)
                return self._browser.playback_select(payload)

            if event_type == "dom.type":
                self._logger.debug("[PLAYBACK EVENT] Text: %s", payload)
                return self._browser.playback_type(payload)

            if event_type == "nav.goto":
                payload = event.get("payload", {})
                url: str = payload.get("url")
                self._logger.debug("[PLAYBACK EVENT] Navigate to '%s'", url)

                try:
                    self._browser.open_page(url)
                except selenium.common.exceptions.WebDriverException as ex:
                    return PlaybackStepResult.fail(f"Unable to navigate to '{url}'")

                return PlaybackStepResult.success()

            if event_type == "rest_api":
                print("REST API : ", event)

                #self._logger.debug("[PLAYBACK EVENT] Wait: %s", event.get("url"))
                #self._browser.open_page(event["url"])
                return PlaybackStepResult.success()

            if event_type == "scroll":
                print(f"Scrolling: {payload}")
                self.perform_page_scroll(event)
                return PlaybackStepResult.success()

            if event_type == "wait":
                self._logger.debug("[PLAYBACK EVENT] Wait: %s ms", payload)
                self._perform_wait(event)
                return PlaybackStepResult.success()

            self._logger.debug("[PLAYBACK EVENT] Unknown event: %s", event_type)
            return PlaybackStepResult.success()

        except Exception as e:  # pylint: disable=broad-exception-caught
            # Absolute last-resort safety net
            self._logger.exception("Playback event crashed")
            return PlaybackStepResult.fail(str(e))

    def _perform_wait(self, event):
        payload = event.get("payload", {})
        duration = payload.get("duration_ms")
        time.sleep(duration / 1000)

    def _perform_rest_api(self, event):
        """
        REST API :  {
            'index': 0,
            'timestamp': 0,
            'type': 'rest_api',
            'payload': {
                'base_url': 'HTTP://localhost:8000',
                'call_type': 'post',
                'rest_call': '/question?ans=yes',
                'body': None
            }
        }
        """

    def perform_page_scroll(self, event):
        payload = event.get("payload", {})
        scroll_type = payload.get("scroll_type")
        scroll_x = payload.get("x_scroll")
        scroll_y = payload.get("y_scroll")

        if scroll_type == "bottom":
            print("Scroll to bottom")
            self._browser.scroll_to_bottom()

        elif scroll_type == "top":
            print("Scroll to top")
            self._browser.scroll_to_top()

        elif scroll_type == "custom":
            print("custom scroll")
            self._browser.scroll_to(int(scroll_x), int(scroll_y))

# ApiClient
