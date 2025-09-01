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
import os
import time
import typing
from selenium.common.exceptions import WebDriverException
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.edge.options import Options as EdgeOptions
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from browser_type import BrowserType
from exceptions import PageLoadError, InvalidBrowserOptionError, \
                       BrowserOptionIncompatibleError, \
                       BrowserOptionMissingParameterError
from web_driver_option_parameters import WebDriverOptionParameters


class WebDriver:
    """
    A wrapper class around Selenium WebDriver that simplifies driver setup
    and provides controlled access to the underlying driver instance.

    This class uses `webdriver_manager` to automatically download and configure
    the correct driver binary for the selected browser.

    Attributes:
        _driver (selenium.webdriver): The internal Selenium WebDriver instance.
    """
    __slots__ = ["_driver", "_screenshots_dir", "_screenshots_enabled"]

    def __init__(self,
                 browser_type: BrowserType = BrowserType.CHROME,
                 parameters: typing.Optional[typing.List] = None,
                 screenshots_enabled: bool = False,
                 screenshots_dir: str = "screenshots"):
        """
        Initialize a WebDriver instance for the specified browser, with optional
        configuration for browser options and automatic screenshot management.

        This constructor wraps Selenium WebDriver and uses `webdriver_manager`
        to automatically download and configure the correct driver binary for
        the selected browser.

        Args:
            browser_type (BrowserType, optional): The type of browser to launch.
                Supported values are `BrowserType.CHROME`, `BrowserType.FIREFOX`,
                and `BrowserType.EDGE`. Defaults to `BrowserType.CHROME`.
            parameters (List, optional): Optional list of browser-specific parameters
                or options. These are parsed internally to configure the browser.
            screenshots_enabled (bool, optional): Whether to enable automatic
                screenshot capture. Defaults to False.
            screenshots_dir (str, optional): Directory where screenshots will be
                saved if `screenshots_enabled` is True. Defaults to `"screenshots"`.

        Raises:
            ValueError: If an unsupported `browser_type` is provided.
            RuntimeError: If the screenshots directory cannot be created due to
                a filesystem error (e.g., permission issues or invalid path).

        Notes:
            - The WebDriver instance is stored in `self._driver` and can be used
              for further Selenium operations.
            - Screenshots are only saved if `screenshots_enabled` is True.
            - The constructor ensures that the screenshots directory exists,
              creating it if necessary.
        """
        self._screenshots_enabled: bool = screenshots_enabled
        self._screenshots_dir: str = screenshots_dir

        if browser_type == BrowserType.CHROME:
            options = self.__parse_options(parameters, browser_type)
            service = ChromeService(ChromeDriverManager().install())
            self._driver = webdriver.Chrome(service=service,
                                            options=options)

        elif browser_type == BrowserType.FIREFOX:
            service = GeckoDriverManager(GeckoDriverManager().install())
            self._driver = webdriver.Firefox(service=service)

        elif browser_type == BrowserType.EDGE:
            service = EdgeService(EdgeChromiumDriverManager().install())
            self._driver = webdriver.Edge(service=service)

        else:
            raise ValueError(f"Unsupported browser: {browser_type.value}")

        try:
            os.makedirs(self._screenshots_dir, exist_ok=True)
        except OSError as e:
            raise RuntimeError(f"Failed to create screenshots directory: {e}") \
                from e

    @property
    def driver(self):
        """
        Provides read-only access to the underlying Selenium WebDriver instance.

        Returns:
            selenium.webdriver: The internal WebDriver object.
        """
        return self._driver

    def open_page(self, url: str):
        """
        Attempt to navigate to the given URL.

        Args:
            url (str): The URL to open.

        Raises:
            PageLoadError: If the page could not be loaded.
        """
        try:
            self._driver.get(url)
        except WebDriverException as e:
            raise PageLoadError(url, e) from e

    def take_screenshot(self, name: str = "screenshot") -> str | None:
        """
        Capture a screenshot of the current browser window and save it to the
        configured screenshots directory.

        The filename will include the provided name and a timestamp to avoid
        collisions, e.g., `screenshot_20250901_225430.png`.

        Args:
            name (str, optional): Base name for the screenshot file.
                Defaults to `"screenshot"`.

        Returns:
            str | None: The full path to the saved screenshot file if screenshots
            are enabled; otherwise, `None`.

        Notes:
            - Screenshots are only taken if `self._screenshots_enabled` is True.
            - The screenshot is saved in PNG format in `self._screenshots_dir`.
            - The method uses a timestamp in `YYYYMMDD_HHMMSS` format for uniqueness.
        """
        if not self._screenshots_enabled:
            return None

        timestamp: str = time.strftime("%Y%m%d_%H%M%S")
        filename: str = os.path.join(self._screenshots_dir,
                                     f"{name}_{timestamp}.png")
        self._driver.save_screenshot(filename)
        return filename

    def __parse_options(self,
                        parameters: list,
                        browser_type: BrowserType):
        if not parameters:
            return None

        if browser_type == BrowserType.CHROME:
            options: ChromeOptions = ChromeOptions()

        elif browser_type == BrowserType.EDGE:
            options: EdgeOptions = EdgeOptions()

        elif browser_type == BrowserType.FIREFOX:
            return None

        else:
            return None

        for param in parameters:
            param_type = param[0]
            param_values = param[1] if len(param) == 2 else None

            if param_type not in WebDriverOptionParameters:
                raise InvalidBrowserOptionError(
                    f"{param_type} for {browser_type}")

            param_entry = WebDriverOptionParameters[param_type]

            if not WebDriverOptionParameters[param_type].is_valid_for(browser_type):
                raise BrowserOptionIncompatibleError(
                    f"{param_type} for {browser_type}")

            arg_name: str = param_entry.get_parameter_for_browser(browser_type)

            if param_entry.has_parameters:
                if not param_values:
                    raise BrowserOptionMissingParameterError(
                        f"{param_type} for {browser_type}")

                option = f"{arg_name}={param_values}"
                options.add_argument(option)

            else:
                options.add_argument(arg_name)

        return options
