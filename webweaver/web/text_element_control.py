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

class TextElementControl(BaseWebControl):
    """
    A web control abstraction for interacting with non-input text elements.

    This class provides read-only access to the visible text content
    of elements such as <span>, <div>, <p>, or <button>.

    Methods
    -------
    get_text() -> str
        Retrieve the visible text of the element.
    """

    def get_text(self) -> str:
        """
        Retrieve the visible text content of the element.

        Returns
        -------
        str
            The visible text of the element.
        """
        text = self._element.text
        if self._logger:
            self._logger.debug("Retrieved element text: %s", text)
        return text
