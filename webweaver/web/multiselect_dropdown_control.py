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


class MultiSelectDropdownControl(BaseDropdownControl):
    """
    A web control abstraction for interacting with multi-select `<select>`
    elements.

    This class extends `BaseWebControl` to provide higher-level operations for
    selecting and deselecting multiple options. It uses Selenium's `Select`
    helper under the hood and validates that the underlying element supports
    multiple selection.

    Examples
    --------
    >>> ms = MultiSelectDropdownControl(driver, logger).attach((By.ID, "fruits"))
    >>> ms.select_by_text("Apple")
    >>> ms.select_by_text("Banana")
    >>> assert set(ms.get_all_selected_texts()) == {"Apple", "Banana"}
    >>> ms.deselect_all()
    """

    @property
    def _select(self) -> Select:
        """
        Lazily create a Selenium `Select` object for the bound element.

        Returns
        -------
        Select
            A Select wrapper for the bound `<select>` element.

        Raises
        ------
        RuntimeError
            If the element is not a multi-select dropdown.
        """
        sel = Select(self._element)
        if not sel.is_multiple:
            raise RuntimeError("Element is not a multi-select dropdown.")
        return sel

    def select_by_text(self, text: str) -> None:
        """Select an option by visible text."""
        if self._logger:
            self._logger.debug("Selecting option by text: %s", text)
        self._select.select_by_visible_text(text)

    def select_by_value(self, value: str) -> None:
        """Select an option by its value attribute."""
        if self._logger:
            self._logger.debug("Selecting option by value: %s", value)
        self._select.select_by_value(value)

    def select_by_index(self, index: int) -> None:
        """Select an option by zero-based index."""
        if self._logger:
            self._logger.debug("Selecting option by index: %d", index)
        self._select.select_by_index(index)

    def deselect_by_text(self, text: str) -> None:
        """Deselect an option by visible text."""
        if self._logger:
            self._logger.debug("Deselecting option by text: %s", text)
        self._select.deselect_by_visible_text(text)

    def deselect_by_value(self, value: str) -> None:
        """Deselect an option by value attribute."""
        if self._logger:
            self._logger.debug("Deselecting option by value: %s", value)
        self._select.deselect_by_value(value)

    def deselect_by_index(self, index: int) -> None:
        """Deselect an option by zero-based index."""
        if self._logger:
            self._logger.debug("Deselecting option by index: %d", index)
        self._select.deselect_by_index(index)

    def deselect_all(self) -> None:
        """Deselect all currently selected options."""
        if self._logger:
            self._logger.debug("Deselecting all options.")
        self._select.deselect_all()

    def get_all_selected_texts(self) -> list[str]:
        """
        Get visible texts of all selected options.

        Returns
        -------
        list[str]
            A list of selected option texts.
        """
        selected = [o.text for o in self._select.all_selected_options]
        if self._logger:
            self._logger.debug("Currently selected options: %s", selected)
        return selected

    def get_all_options(self) -> list[str]:
        """
        Get visible texts of all available multi-select options.

        Returns
        -------
        list[str]
            A list of all option texts in the dropdown.
        """
        return self._get_options_text(self._select)
