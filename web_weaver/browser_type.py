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


class BrowserType(enum.Enum):
    """
    Enum representing the supported browser types for Selenium WebDriver.

    This enumeration is intended to be used when initializing the
    :class:`WebDriver` wrapper, ensuring type safety and readability
    instead of passing raw strings.

    Members:
        CHROME: Google Chrome browser.
        FIREFOX: Mozilla Firefox browser.
        EDGE: Microsoft Edge browser.
    """
    CHROME = enum.auto()
    FIREFOX = enum.auto()
    EDGE = enum.auto()
