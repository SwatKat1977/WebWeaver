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

class TestSuitePlaybackSession:

    def __init__(self,
                 browser: StudioBrowser,
                 recording: Recording,
                 logger: Logger):
        self._browser = browser
        self._recording = recording
        self._index = 0
        self._running = False
        self._logger = logger.getChild(__name__)
        # self.callback_events = PlaybackCallbackEvents()
        self._thread = None
        self._engine: PlaybackEngine = PlaybackEngine(browser,
                                                      recording,
                                                      logger)
