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
from dataclasses import dataclass
from typing import List, Optional, Union, Tuple
from webweaver.web.browser_type import BrowserType
from webweaver.web.web_driver_option import WebDriverOption

BrowserOption = Union[Tuple[WebDriverOption], Tuple[WebDriverOption, str]]


@dataclass
class WebWeaverConfig:
    """
    Configuration model for setting up the test environment and browser.

    Attributes:
        browser_type (BrowserType): Enum specifying which browser to use.
        browser_options (Optional[List[tuple]]): Browser-specific options like
                                                 headless mode.
        screenshots_enabled (bool): Whether to take screenshots on failure.
        screenshots_dir (str): Directory where screenshots should be saved.
        log_level (str): Logging verbosity (e.g., 'DEBUG', 'INFO', 'WARNING').
    """
    browser_type: BrowserType
    browser_options: Optional[List[BrowserOption]] = None
    screenshots_enabled: bool = False
    screenshots_dir: str = "screenshots"
    log_level: str = "INFO"
