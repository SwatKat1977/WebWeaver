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
from browsing.studio_browser import PlaybackStepResult, StudioBrowser
from recording.recording import Recording


class RecordingPlaybackSession:
    """
    Executes a recorded WebWeaver recording step-by-step using a StudioBrowser.
    """

    def __init__(self, browser: StudioBrowser, recording: Recording):
        self._browser = browser
        self._recording = recording
        self._index = 0
        self._running = False

    def start(self):
        self._running = True
        self._index = 0

    def stop(self):
        self._running = False

    def step(self) -> bool:
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
        event_type = event.get("type")
        payload = event.get("payload", {})

        if event_type == "dom.check":
            print(f"[EVENT] Check: {payload}")

        elif event_type == "dom.click":
            print(f"=> Clicking: {payload}")
            return self._browser.playback_click(payload)

        elif event_type == "nav.goto":
            self._browser.open_page(event["url"])

        elif event_type == "dom.select":
            print(f"[EVENT] Select: {payload}")

        elif event_type == "dom.type":
            print(f"[EVENT] Type: {payload}")

        else:
            print("Unknown event:", event_type)

        return PlaybackStepResult(ok=True, error="")
