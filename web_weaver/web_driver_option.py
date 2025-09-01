"""
This source file is part of Web Weaver
For the latest info, see https://github.com/SwatKat1977/WebWeaver

Copyright 2025 SwatKat1977

    This program is free software : you can redistribute it and /or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.If not, see < https://www.gnu.org/licenses/>.
"""
import enum


class WebDriverOption(enum.Enum):
    """
    Enumeration of common WebDriver configuration options.

    These options can be applied when launching a browser instance with
    Selenium framework. They control the behavior, appearance, and privacy of
    the browser session.
    """
    HEADLESS = enum.auto()
    """Run the browser in headless mode (without a visible UI)."""

    DISABLE_EXTENSIONS = enum.auto()
    """Disable all installed browser extensions during the session."""

    DISABLE_GPU = enum.auto()
    """Disable GPU hardware acceleration (useful for headless environments)."""

    MAXIMISED = enum.auto()
    """Launch the browser window in maximized mode."""

    PRIVATE = enum.auto()
    """Open the browser in private/incognito mode to avoid storing history or
       cookies."""

    DISABLE_POPUP_BLOCKING = enum.auto()
    """Turn off the browser's built-in popup blocking feature."""

    WINDOW_SIZE = enum.auto()
    """Set a custom initial window size for the browser session."""

    DISABLE_NOTIFICATIONS = enum.auto()
    """Suppress browser notifications (e.g., push notifications)."""

    REMOTE_DEBUGGING_PORT = enum.auto()
    """Enable remote debugging via a specified port for developer tools or
       automation."""

    LOG_LEVEL = enum.auto()
