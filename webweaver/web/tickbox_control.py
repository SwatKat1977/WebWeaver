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
from base_web_control import BaseWebControl


class TickboxControl(BaseWebControl):
    """
    A web control abstraction for interacting with checkbox (tickbox) elements.

    This class extends `BaseWebControl` to provide higher-level operations for
    checkboxes, such as checking, unchecking, and toggling their state. It uses
    Selenium WebDriver under the hood and logs all significant interactions
    for easier debugging.

    Methods
    -------
    is_toggled() -> bool
        Returns whether the checkbox is currently selected (checked).
    toggle() -> None
        Clicks the checkbox element to toggle its state.
    check() -> None
        Ensures the checkbox is checked; toggles it only if it is unchecked.
    uncheck() -> None
        Ensures the checkbox is unchecked; toggles it only if it is checked.
    """

    def is_toggled(self) -> bool:
        """
        Check whether the checkbox is currently selected.

        Returns
        -------
        bool
            True if the checkbox is selected (checked), False otherwise.
        """
        state = self._element.is_selected()
        if self._logger:
            self._logger.debug("Checkbox state: %s", state)

        return state

    def toggle(self):
        """
        Toggle the checkbox state by clicking on it.

        Notes
        -----
        This method flips the current state:
        - If checked, it will be unchecked.
        - If unchecked, it will be checked.
        """
        if self._logger:
            self._logger.debug("Toggling checkbox at locator: %s", self._element)

        self._element.click()

    def check(self):
        """
        Ensure the checkbox is checked.

        If the checkbox is not already selected, it will be toggled to the
        checked state. If it is already checked, no action is taken.
        """
        if not self.is_toggled():
            if self._logger:
                self._logger.debug("Checking checkbox (currently unchecked).")

            self.toggle()

    def uncheck(self):
        """
        Ensure the checkbox is unchecked.

        If the checkbox is currently selected, it will be toggled to the
        unchecked state. If it is already unchecked, no action is taken.
        """
        if self.is_toggled():
            if self._logger:
                self._logger.debug("Unchecking checkbox (currently checked).")

            self.toggle()
