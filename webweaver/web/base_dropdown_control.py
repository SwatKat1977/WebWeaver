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
from web.base_web_control import BaseWebControl


class BaseDropdownControl(BaseWebControl):
    """
    Base class for dropdown controls.

    Provides shared utility methods for extracting option text values
    from Selenium ``Select`` elements. Designed to be inherited by
    specific dropdown implementations (e.g., single-select or multi-select).

    Parameters
    ----------
    logger : logging.Logger, optional
        Logger instance for emitting debug information. If ``None``,
        no logging is performed.
    """
    #pylint: disable=too-few-public-methods

    def _get_options_text(self, select) -> list[str]:
        """
        Extract the visible text from all options in a ``Select`` element.

        Parameters
        ----------
        select : selenium.webdriver.support.ui.Select
            The Selenium ``Select`` object representing the dropdown.

        Returns
        -------
        list[str]
            A list containing the text of each available option.
        """
        options = [o.text for o in select.options]
        if self._logger:
            self._logger.debug("Available dropdown options: %s", options)
        return options
