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
from selenium.common.exceptions import WebDriverException
from web.base_web_control import BaseWebControl


class RadioButtonControl(BaseWebControl):
    """
    Control for interacting with radio button groups.
    """

    def select(self) -> bool:
        """
        Select a radio button from a group.

        Returns
        -------
        bool
            True if selection succeeded, False otherwise.
        """
        if self._element:
            try:
                self._element.click()
                return True

            except WebDriverException  as e:
                self._logger.error(f"Failed to click radio button {self._element}: {e}")

        return False

    def is_selected(self) -> bool:
        """
        Check whether a specific radio button is selected.

        Parameters
        ----------
        name : str
            The ``name`` attribute shared by the radio group.
        value : str
            The ``value`` attribute of the radio button to check.
        timeout : int, optional
            Maximum seconds to wait for the element (default 10).

        Returns
        -------
        bool
            True if selected, False otherwise.
        """
        return self._element.is_selected() if self._element else False
