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
from typing import Dict, List, Optional
from .browser_type import BrowserType
from .web_driver_option import WebDriverOption
from .web_driver_option_binding import WebDriverOptionBinding


class WebDriverOptionParameter:
    """
    Describes how a single high-level WebDriverOption is applied across different browsers.

    This class acts as the metadata and binding container for one abstract launch option.
    It defines:

    - Which browsers support the option
    - How the option is applied for each supported browser
    - Whether the option accepts an additional parameter value

    Each instance of this class is typically stored in the WebDriverOptionParameters
    registry, which serves as the central translation table between abstract launch
    options and concrete Selenium configuration operations.

    Conceptually, this represents one row in the "option compiler" table:

        Abstract option → Browser-specific bindings → Concrete WebDriver settings
    """

    def __init__(
        self,
        option: WebDriverOption,
        valid_for: Dict[BrowserType, List[WebDriverOptionBinding]],
        has_parameters: bool = False):
        """
        Create a new WebDriverOptionParameter definition.

        :param option: The abstract WebDriverOption this definition describes.
        :param valid_for: A mapping of BrowserType to a list of bindings describing how
                          this option should be applied for that browser.
        :param has_parameters: Whether this option requires or accepts a parameter value
                               (e.g. window size, user agent).
        """
        self._option = option
        self._valid_for = valid_for
        self._has_parameters = has_parameters

    def bindings_for(self, browser: BrowserType) -> \
            Optional[List[WebDriverOptionBinding]]:
        """
        Get the list of bindings used to apply this option for a specific browser.

        :param browser: The browser type to query.
        :return: A list of WebDriverOptionBinding instances, or None if the option is not
                 supported for the specified browser.
        """
        return self._valid_for.get(browser)

    @property
    def option(self) -> WebDriverOption:
        """
        Get the abstract WebDriverOption this parameter definition describes.
        """
        return self._option

    @property
    def has_parameters(self) -> bool:
        """
        Indicates whether this option accepts or requires a parameter value.
        """
        return self._has_parameters

    def is_valid_for(self, browser: BrowserType) -> bool:
        """
        Check whether this option is supported for the specified browser.

        :param browser: The browser type to check.
        :return: True if the option can be applied to this browser, otherwise
                 False.
        """
        return browser in self._valid_for
