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


class WebDriverOptionTarget(enum.Enum):
    """
    Enumeration of concrete WebDriver configuration targets for launch options.

    This enum describes *how* a high-level browser launch option should be applied to
    a specific browser configuration. Each value represents a different mechanism used
    by Selenium and the underlying browser engines to receive configuration data.

    It is used by the WebDriverOptionParameters binding system to decide where and how
    a particular option value should be written.

    Targets:
        ARGUMENT:
            Apply the option as a command-line argument to a Chromium-based browser
            (e.g. "--headless", "--user-data-dir=...").

        CHROMIUM_PREF:
            Apply the option as a Chromium preference via the browser's experimental
            options dictionary (used by Chrome, Chromium, and Edge).

        FIREFOX_PREF:
            Apply the option as a Firefox profile preference.
    """
    ARGUMENT = enum.auto()
    CHROMIUM_PREF = enum.auto()
    FIREFOX_PREF = enum.auto()
