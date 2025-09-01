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


class PageLoadError(Exception):
    """Custom exception raised when a page cannot be loaded."""
    def __init__(self, url: str, original_exception: Exception):
        self.url = url
        self.original_exception = original_exception
        super().__init__(f"Failed to load page: {url} ({original_exception})")

class InvalidBrowserOptionError(Exception):
    """
    Raised when an unsupported or unrecognized WebDriver option is provided.

    This exception indicates that the given option does not exist in the
    set of known `WebDriverOption` values.

    Parameters
    ----------
    exception_str : str
        The error message describing the invalid option.
    """
    def __init__(self, exception_str: str):
        super().__init__(exception_str)

class BrowserOptionIncompatibleError(Exception):
    """
    Raised when a valid WebDriver option is not supported by the selected browser.

    This exception occurs when an option exists but cannot be applied
    to the current `BrowserType`.

    Parameters
    ----------
    exception_str : str
        The error message describing the incompatibility.
    """
    def __init__(self, exception_str: str):
        super().__init__(exception_str)

class BrowserOptionMissingParameterError(Exception):
    """
    Raised when a WebDriver option requires parameters but none are provided.

    For example, an option like `--window-size` requires width and height
    values; if they are missing, this exception is raised.

    Parameters
    ----------
    exception_str : str
        The error message describing the missing parameter.
    """
    def __init__(self, exception_str: str):
        super().__init__(exception_str)
