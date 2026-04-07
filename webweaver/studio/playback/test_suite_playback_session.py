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
from webweaver.studio.playback.playback_session_base import PlaybackSessionBase
from webweaver.studio.test_suites.test_suite import TestSuite

class TestSuitePlaybackSession(PlaybackSessionBase):

    def __init__(self,
                 browser: StudioBrowser,
                 suite: TestSuite,
                 logger: Logger):
        super().__init__(logger)
        self._browser = browser
        self._suite = suite
        # self._engine: PlaybackEngine = PlaybackEngine(browser,
        #                                               recording,
        #                                               logger)

    def _get_step_count(self):
        return 0
        # return len(self._suite. steps)

    def _execute_step(self, index):
        return
        # step = self._suite.steps[index]
        # return self._engine.execute_test(step)
