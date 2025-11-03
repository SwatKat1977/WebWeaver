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
from selenium.webdriver.support.ui import Select
from web.base_dropdown_control import BaseDropdownControl


class DropdownControl(BaseDropdownControl):
    """
    A web control abstraction for interacting with `<select>` dropdowns.

    The `Select` helper is created on-demand from the bound element.

    Examples
    --------
    >>> dd = DropdownControl(driver, logger).find_element_by_id("country")
    >>> dd.select_by_text("United Kingdom")
    >>> assert dd.get_selected_text() == "United Kingdom"
    """

    @property
    def _select(self) -> Select:
        """
        Lazily create a Selenium `Select` for the bound element.

        Returns
        -------
        Select
            The Select wrapper for the bound `<select>` element.
        """
        return Select(self._element)

    def select_by_text(self, text: str) -> None:
        """
        Select an option by visible text.

        Parameters
        ----------
        text : str
            The visible text to select.
        """
        if self._logger:
            self._logger.debug("Selecting dropdown option by text: %s", text)
        self._select.select_by_visible_text(text)

    def select_by_value(self, value: str) -> None:
        """
        Select an option by value attribute.

        Parameters
        ----------
        value : str
            The `value` attribute of the option to select.
        """
        if self._logger:
            self._logger.debug("Selecting dropdown option by value: %s", value)
        self._select.select_by_value(value)

    def select_by_index(self, index: int) -> None:
        """
        Select an option by zero-based index.

        Parameters
        ----------
        index : int
            The index to select.
        """
        if self._logger:
            self._logger.debug("Selecting dropdown option by index: %d", index)
        self._select.select_by_index(index)

    def get_selected_text(self) -> str:
        """
        Return the visible text of the currently selected option.

        Returns
        -------
        str
            The selected option's text.
        """
        selected = self._select.first_selected_option.text
        if self._logger:
            self._logger.debug("Currently selected option: %s", selected)
        return selected

    def get_all_options(self) -> list[str]:
        """
        Return the visible text for all options.

        Returns
        -------
        list[str]
            All option texts in the dropdown.
        """
        return self._get_options_text(self._select)
