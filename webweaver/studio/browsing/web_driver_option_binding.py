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
from .web_driver_option_target import WebDriverOptionTarget


@dataclass(frozen=True)
class WebDriverOptionBinding:
    """
    Represents a single concrete binding between an abstract WebDriver option and a
    browser-specific configuration mechanism.

    A binding describes:

    - Where an option should be applied (the target)
    - The concrete key, flag, or preference name to use

    This is the smallest unit in the WebDriver option translation system. Higher-level
    structures (such as WebDriverOptionParameter and the WebDriverOptionParameters
    registry) combine multiple bindings to describe how a single abstract option should
    be applied across different browsers.

    Examples:
        - (ARGUMENT, "--disable-extensions")
        - (CHROMIUM_PREF, "profile.default_content_setting_values.notifications")
        - (FIREFOX_PREF, "permissions.default.desktop-notification")
    """
    target: WebDriverOptionTarget
    key: str
