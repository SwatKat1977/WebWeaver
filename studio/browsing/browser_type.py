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


class BrowserType(enum.Enum):
    """
    Enumeration of supported browser types that can be used by the WebDriver.

    This enum is used to select which browser engine should be launched or
    controlled by the automation system.

    Members:
        CHROME:
            Google Chrome browser.

        CHROMIUM:
            Chromium-based browser (open-source Chrome variant or compatible
            builds).

        EDGE:
            Microsoft Edge browser (Chromium-based).

        FIREFOX:
            Mozilla Firefox browser.
    """

    CHROME = enum.auto()
    CHROMIUM = enum.auto()
    EDGE = enum.auto()
    FIREFOX = enum.auto()
