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
from __future__ import annotations
from typing import TYPE_CHECKING
import enum
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions

if TYPE_CHECKING:
    from webweaver.web.web_driver import WebDriver


class ElementSelectorType(enum.Enum):
    SELECTOR_ID = By.ID
    SELECTOR_CSS_SELECTOR = By.CSS_SELECTOR
    SELECTOR_XPATH = By.XPATH
    SELECTOR_NAME = By.NAME
    SELECTOR_TAG_NAME = By.TAG_NAME


class WebWeaverPage:
    """
    A base page-object wrapper for interacting with a web page using a
    Selenium-like driver.

    This class provides common browser actions such as scrolling, retrieving
    page metadata, refreshing, and waiting for elements to reach specific
    states.
    """

    def __init__(self, driver: WebDriver):
        """
        Initialize the WebWeaverPage.

        Parameters
        ----------
        driver : object
            A wrapper object containing a Selenium WebDriver instance
            accessible via `driver.driver`.
        """
        self._driver: WebDriver = driver

    def scroll_to_bottom(self):
        """
        Scroll the browser window to the bottom of the current page.
        """
        self._driver.driver.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);")

    def scroll_to_top(self):
        """
        Scroll the browser window to the top of the current page.
        """
        self._driver.driver.execute_script("window.scrollTo(0, 0);")

    def scroll_to(self, x, y):
        """
        Scroll the browser window to a specific position.

        Parameters
        ----------
        x : int
            The horizontal scroll offset.
        y : int
            The vertical scroll offset.
        """
        self._driver.driver.execute_script(f"window.scrollTo({x}, {y});")

    def get_title(self):
        """
        Get the current page's title.

        Returns
        -------
        str
            The title of the current web page.
        """
        return self._driver.driver.title

    def get_url(self):
        """
        Get the current page URL.

        Returns
        -------
        str
            The URL of the current page.
        """
        return self._driver.driver.current_url

    def refresh(self):
        """
        Refresh the current page.
        """
        self._driver.driver.refresh()

    def wait_for_visible(self,
                         selector: ElementSelectorType,
                         value: str,
                         timeout: int = 10):
        """
        Wait until an element becomes visible on the page.

        Parameters
        ----------
        selector : ElementSelectorType
            The type of selector used (e.g., CSS_SELECTOR, XPATH).
        value : str
            The selector value.
        timeout : int, optional
            Maximum time (in seconds) to wait, by default 10.

        Returns
        -------
        WebElement
            The located element once it becomes visible.
        """
        return WebDriverWait(self._driver.driver, timeout).until(
            expected_conditions.visibility_of_element_located((selector.value, value))
        )

    def wait_for_present(self,
                         selector: ElementSelectorType,
                         value: str,
                         timeout: int = 10):
        """
        Wait until an element is present in the DOM.

        Parameters
        ----------
        selector : ElementSelectorType
            The type of selector used.
        value : str
            The selector value.
        timeout : int, optional
            Maximum wait time, by default 10 seconds.

        Returns
        -------
        WebElement
            The located element once it is present in the DOM.
        """
        return WebDriverWait(self._driver.driver, timeout).until(
            expected_conditions.presence_of_element_located((selector.value, value))
        )

    def wait_for_clickable(self,
                           selector: ElementSelectorType,
                           value: str,
                           timeout: int = 10):
        """
        Wait until an element becomes clickable.

        Parameters
        ----------
        selector : ElementSelectorType
            The type of selector used.
        value : str
            The selector value.
        timeout : int, optional
            Maximum wait time, by default 10 seconds.

        Returns
        -------
        WebElement
            The located element once it is clickable.
        """
        return WebDriverWait(self._driver.driver, timeout).until(
            expected_conditions.element_to_be_clickable((selector.value, value))
        )
