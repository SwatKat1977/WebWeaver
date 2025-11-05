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
import logging
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.common.exceptions import NoSuchElementException, \
                                       TimeoutException, \
                                       StaleElementReferenceException
from selenium.webdriver.common.by import By
from web.web_driver import WebDriver


class BaseWebControl:
    """
    Base class for web controls that interact with a Selenium WebDriver instance.

    This class provides a foundation for building higher-level control abstractions
    (e.g., buttons, text boxes, dropdowns) that operate on web elements through a
    Selenium WebDriver. It also integrates logging by creating a child logger
    specific to this module.

    Attributes
    ----------
    _driver : WebDriver
        The Selenium WebDriver instance used to interact with the browser.
    _logger : logging.Logger
        A child logger derived from the provided logger, namespaced to this module.
    """
    __slot__ = ["_driver", "_logger"]

    def __init__(self, driver: WebDriver, logger: logging.Logger):
        """
        Initialize the BaseWebControl.

        Parameters
        ----------
        driver : WebDriver
            A Selenium WebDriver instance used to control the browser.
        logger : logging.Logger
            A base logger from which a child logger will be created for this class.
        """
        self._driver: WebDriver = driver
        self._logger = logger.getChild(__name__)
        self._element = None

    def find_element_by_id(self,
                           value,
                           timeout: int = 10,
                           retries: int = 2,
                           screenshot_on_fail: bool = False):
        """
        Locate a web element by its HTML ``id`` attribute.

        Parameters
        ----------
        value : str
            The ``id`` attribute of the element to locate.
        timeout : int, optional
            Maximum number of seconds to wait for the element (default is 10).
        retries : int, optional
            Number of retries if the element reference becomes stale (default is 2).
        screenshot_on_fail : bool, optional
            If True, take a screenshot when the element cannot be found or
            when all retries have been exhausted (default is False).

        Returns
        -------
        WebElement | None
            The located element, or None if not found.
        """
        return self.__find_element(By.ID,
                                   value,
                                   timeout,
                                   retries,
                                   screenshot_on_fail)

    def find_element_by_xpath(self,
                              value: str,
                              timeout: int = 10,
                              retries: int = 2,
                              screenshot_on_fail: bool = False):
        """
        Locate a web element using an XPath expression.

        Parameters
        ----------
        value : str
            The XPath expression of the element to locate.
        timeout : int, optional
            Maximum number of seconds to wait for the element (default is 10).
        retries : int, optional
            Number of retries if the element reference becomes stale (default is 2).
        screenshot_on_fail : bool, optional
            If True, take a screenshot when the element cannot be found or
            when all retries have been exhausted (default is False).

        Returns
        -------
        WebElement | None
            The located element, or None if not found.
        """
        return self.__find_element(By.XPATH,
                                   value,
                                   timeout,
                                   retries,
                                   screenshot_on_fail)

    def find_element_by_class_name(self,
                                   value: str,
                                   timeout: int = 10,
                                   retries: int = 2,
                                   screenshot_on_fail: bool = False):
        """
        Locate a web element by its ``class`` attribute.

        Parameters
        ----------
        value : str
            The class name of the element to locate.
        timeout : int, optional
            Maximum number of seconds to wait for the element (default is 10).
        retries : int, optional
            Number of retries if the element reference becomes stale (default is 2).
        screenshot_on_fail : bool, optional
            If True, take a screenshot when the element cannot be found or
            when all retries have been exhausted (default is False).

        Returns
        -------
        WebElement | None
            The located element, or None if not found.
        """
        return self.__find_element(By.CLASS_NAME,
                                   value,
                                   timeout,
                                   retries,
                                   screenshot_on_fail)

    def find_element_by_css(self,
                            value: str,
                            timeout: int = 10,
                            retries: int = 2,
                            screenshot_on_fail: bool = False):
        """
        Locate a web element using a CSS selector.

        Parameters
        ----------
        value : str
            The CSS selector string of the element to locate.
        timeout : int, optional
            Maximum number of seconds to wait for the element (default is 10).
        retries : int, optional
            Number of retries if the element reference becomes stale (default is 2).
        screenshot_on_fail : bool, optional
            If True, take a screenshot when the element cannot be found or
            when all retries have been exhausted (default is False).

        Returns
        -------
        WebElement | None
            The located element, or None if not found.
        """
        return self.__find_element(By.CSS_SELECTOR,
                                   value,
                                   timeout,
                                   retries,
                                   screenshot_on_fail)

    def __find_element(self,
                       by,
                       value,
                       timeout: int,
                       retries: int,
                       screenshot_on_fail: bool):
        """
        Safely locate an element with retries and explicit wait.

        Parameters
        ----------
        by : selenium.webdriver.common.by.By
            Locator strategy (e.g., By.ID, By.CSS_SELECTOR).
        value : str
            The actual locator string.
        timeout : int, optional
            Max time (seconds) to wait for the element to appear.
        retries : int, optional
            Number of times to retry if element goes stale.

        Returns
        -------
        WebElement | None
            The located element, or None if not found.
        """
        # pylint: disable=too-many-positional-arguments, too-many-arguments
        attempt = 0

        while attempt <= retries:
            try:
                self._logger.debug(f"Looking for element by {by}='{value}' (attempt {attempt+1})")
                element = WebDriverWait(self._driver.driver, timeout).until(
                    expected_conditions.presence_of_element_located((by,
                                                                     value))
                )
                self._element = element
                return element
            except (TimeoutException, NoSuchElementException) as e:
                self._logger.warning(f"Element not found: {by}='{value}', error={e}")
                return None
            except StaleElementReferenceException:
                self._logger.warning(f"Stale element reference for {by}='{value}', retrying...")
                attempt += 1

        self._logger.error(f"Failed to locate stable element after {retries} "
                           f"retries: {by}='{value}'")
        if screenshot_on_fail:
            filename = self._driver.take_screenshot(f"fail_{value}")
            self._logger.info(f"Screenshot saved to {filename} due to failure")
        return None
