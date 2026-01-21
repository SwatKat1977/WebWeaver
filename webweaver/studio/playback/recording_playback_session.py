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
from browsing.studio_browser import StudioBrowser
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

    def step(self):
        if not self._running:
            return

        if self._index >= len(self._recording.events):
            self.stop()
            return

        ev = self._recording.events[self._index]
        self._execute_event(ev)
        self._index += 1

    def _execute_event(self, ev: dict):
        kind = ev.get("__kind")

        if kind == "click":
            self._browser.playback_click(ev)

        elif kind == "nav.goto":
            self._browser.open_page(ev["url"])

        else:
            print("Unknown event:", kind)
