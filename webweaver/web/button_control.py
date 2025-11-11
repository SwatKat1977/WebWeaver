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
from webweaver.web.base_web_control import BaseWebControl


class ButtonControl(BaseWebControl):
    """
    Control for interacting with buttons or clickable elements.
    """

    def click(self) -> bool:
        """
        Click a button (or button-like element).

        Returns
        -------
        bool
            True if the button was clicked, False otherwise.
        """

        if self._element is not None:
            try:
                self._element.click()
                return True

            except WebDriverException as e:
                self._logger.error(
                    f"Failed to click button {self._element}: {e}")

        return False
