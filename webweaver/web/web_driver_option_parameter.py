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
import typing
from browser_type import BrowserType
from web_driver_option import WebDriverOption


class WebDriverOptionParameter:
    """
    Represents a configurable WebDriver option, including its parameters
    and browser compatibility.

    This class encapsulates a specific option from ``WebDriverOption``,
    whether it accepts parameters, and which browser types support it.

    Attributes
    ----------
    _option : WebDriverOption
        The WebDriver option being represented.
    _params : bool
        Whether this option requires or supports parameters (e.g.,
        window size dimensions).
    _valid_for : dict[BrowserType, bool]
        A mapping indicating which browsers support this option.
        Typically, the dictionary keys are browser types and the values
        indicate compatibility (``True`` if supported).
    """
    __slots__ = ['_option', '_params', '_valid_for']

    def __init__(self,
                 option: WebDriverOption,
                 valid_for: typing.Dict,
                 params: bool = False):
        """
        Initialize a WebDriverOptionParameter instance.

        Parameters
        ----------
        option : WebDriverOption
            The WebDriver option to represent.
        valid_for : dict[BrowserType, bool]
            Dictionary mapping browser types to whether they support
            this option.
        params : bool, optional
            Whether the option requires parameters (default is False).
        """
        self._option = option
        self._params = params
        self._valid_for = valid_for

    @property
    def option(self) -> WebDriverOption:
        """
        Get the WebDriver option.

        Returns
        -------
        WebDriverOption
            The option associated with this parameter object.
        """
        return self._option

    @property
    def has_parameters(self) -> bool:
        """
        Check whether the option accepts parameters.

        Returns
        -------
        bool
            True if the option requires or supports parameters,
            otherwise False.
        """
        return self._params

    def is_valid_for(self, browser: BrowserType) -> bool:
        """
        Check whether the option is valid for a given browser.

        Parameters
        ----------
        browser : BrowserType
            The browser type to check compatibility for.

        Returns
        -------
        bool
            True if the option is supported by the given browser,
            otherwise False.
        """
        return browser in self._valid_for

    def get_parameter_for_browser(self, browser: BrowserType) -> str:
        """
        Retrieve the option argument string for a given browser.

        Parameters
        ----------
        browser : BrowserType
            The browser type for which to get the parameter string.

        Returns
        -------
        str or None
            The option string specific to the browser if supported,
            otherwise None.
        """
        if not browser in self._valid_for:
            return None

        return self._valid_for[browser]
