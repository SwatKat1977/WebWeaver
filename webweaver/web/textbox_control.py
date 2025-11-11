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
from webweaver.web.base_web_control import BaseWebControl


class TextboxControl(BaseWebControl):
    """
    A web control abstraction for interacting with text box (input) elements.

    This class extends `BaseWebControl` to provide higher-level operations
    for text boxes, such as entering text, clearing input, and retrieving
    the current value. It uses Selenium WebDriver under the hood and logs
    all significant interactions for easier debugging.

    Methods
    -------
    get_value() -> str
        Retrieve the current value of the text box.
    set_value(text: str) -> None
        Clear the text box and enter the specified text.
    clear() -> None
        Clear the contents of the text box.
    append(text: str) -> None
        Append text to the current value of the text box without clearing.
    """

    def get_value(self) -> str:
        """
        Retrieve the current value from the text box.

        Returns
        -------
        str
            The current value (text) in the text box.
        """
        value = self._element.get_attribute("value")
        if self._logger:
            self._logger.debug("Retrieved textbox value: %s", value)
        return value

    def set_value(self, text: str):
        """
        Clear the text box and set it to the provided text.

        Parameters
        ----------
        text : str
            The text to input into the text box.
        """
        if self._logger:
            self._logger.debug("Setting textbox value to: %s", text)
        self.clear()
        self._element.send_keys(text)

    def clear(self):
        """
        Clear the contents of the text box.

        Notes
        -----
        Uses Selenium's `clear()` method on the element.
        """
        if self._logger:
            self._logger.debug("Clearing textbox.")
        self._element.clear()

    def append(self, text: str):
        """
        Append text to the existing value in the text box.

        Parameters
        ----------
        text : str
            The text to append to the current value.
        """
        if self._logger:
            self._logger.debug("Appending '%s' to textbox.", text)
        self._element.send_keys(text)
