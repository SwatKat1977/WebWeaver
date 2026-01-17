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
import enum


class WebDriverOption(enum.Enum):
    """
    Enumeration of configuration options that can be applied to a WebDriver
    instance when launching or configuring a browser.

    Each option represents a common toggle or setting that influences browser
    behavior, privacy, appearance, or compatibility.

    Members:
        DISABLE_EXTENSIONS:
            Disable all browser extensions.

        DISABLE_NOTIFICATIONS:
            Prevent websites and the browser from showing notifications.

        IGNORE_CERTIFICATE_ERROR:
            Ignore SSL / certificate errors (useful for testing against
            self-signed or invalid certificates).

        PRIVATE:
            Launch the browser in private / incognito mode.

        USER_AGENT:
            Override the browser's default user agent string.

        WINDOW_SIZE:
            Set a specific window size for the browser.

        MAXIMISED:
            Start the browser window maximised.
    """

    DISABLE_EXTENSIONS = enum.auto()
    DISABLE_NOTIFICATIONS = enum.auto()
    IGNORE_CERTIFICATE_ERROR = enum.auto()
    PRIVATE = enum.auto()
    USER_AGENT = enum.auto()
    WINDOW_SIZE = enum.auto()
    MAXIMISED = enum.auto()
