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


class WebWeaverPage:
    def __init__(self, driver):
        self._driver = driver

    def scroll_to_bottom(self):
        self._driver.driver.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);")

    def scroll_to_top(self):
        self._driver.driver.execute_script("window.scrollTo(0, 0);")

    def scroll_to(self, x, y):
        self._driver.execute_script(f"window.scrollTo({x}, {y});")

    def get_title(self):
        return self._driver.driver.title

    def get_url(self):
        return self._driver.driver.current_url

    def refresh(self):
        self._driver.driver.refresh()
