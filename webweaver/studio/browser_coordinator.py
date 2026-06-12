"""
This source file is part of Web Weaver
For the latest info, see https://github.com/SwatKat1977/WebWeaver

Copyright 2025-2026 SwatKat1977

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
import threading
from typing import Optional
from selenium.common.exceptions import WebDriverException
from webweaver.studio.browsing.studio_browser import StudioBrowser
from webweaver.studio.browsing.web_driver_factory import create_driver_from_solution
from webweaver.studio.studio_solution import StudioSolution


class BrowserCoordinator:
    """
    Owns the lifecycle of the integrated web browser.

    The coordinator has no wx dependencies — all dialogs and UI updates are
    the caller's responsibility.  Methods that can fail return plain
    ``(ok, error_message)`` tuples.
    """

    def __init__(self, logger: logging.Logger) -> None:
        self._web_browser: Optional[StudioBrowser] = None
        self._logger = logger

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def browser(self) -> Optional[StudioBrowser]:
        """The active browser instance, or None."""
        return self._web_browser

    # ------------------------------------------------------------------
    # Status
    # ------------------------------------------------------------------

    def is_open(self) -> bool:
        """True if a browser instance exists (it may not be responsive)."""
        return self._web_browser is not None

    def is_alive(self) -> bool:
        """True if a browser instance exists and is responsive."""
        return self._web_browser is not None and self._web_browser.is_alive()

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def open(self, solution: StudioSolution) -> tuple[bool, str]:
        """Create a WebDriver from the solution config and navigate to its base URL.

        On failure, any partially-created browser instance is cleaned up.

        Returns:
            ``(True, "")`` on success, or ``(False, error_message)`` on failure.
        """
        try:
            self._web_browser = create_driver_from_solution(solution, self._logger)
            self._web_browser.open_page(solution.base_url)
            return True, ""
        except WebDriverException as exc:
            if self._web_browser and self._web_browser.is_alive():
                self._web_browser.quit()
            self._web_browser = None
            return False, str(exc.msg)

    def close(self) -> None:
        """Synchronously close the browser.

        Safe to call when no browser is open or when the browser is no longer
        alive — exceptions from ``quit()`` are suppressed.
        """
        if self._web_browser:
            try:
                self._web_browser.quit()
            except WebDriverException:
                pass
            self._web_browser = None

    def close_async(self) -> None:
        """Close the browser in a background daemon thread.

        Use this when closing on the UI thread would cause a noticeable freeze
        (e.g. during solution close).  The internal reference is nulled
        immediately so subsequent calls see no browser.
        """
        browser = self._web_browser
        self._web_browser = None
        if browser and browser.is_alive():
            threading.Thread(
                target=self._close_safely,
                args=(browser,),
                daemon=True,
            ).start()

    def detach(self) -> None:
        """Discard the browser reference without calling quit().

        Use when the browser process has already terminated externally (e.g.
        the user closed the browser window) so there is nothing to quit.
        """
        self._web_browser = None

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _close_safely(self, browser: StudioBrowser) -> None:
        try:
            browser.quit()
        except WebDriverException:
            pass
