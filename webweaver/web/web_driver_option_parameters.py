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
from browser_type import BrowserType
from web_driver_option import WebDriverOption
from web_driver_option_parameter import WebDriverOptionParameter

WebDriverOptionParameters: dict = {
    WebDriverOption.HEADLESS: WebDriverOptionParameter(
        WebDriverOption.HEADLESS,
        {
            BrowserType.CHROME: "--headless",
            BrowserType.EDGE: "--headless"
        }
    ),
    WebDriverOption.DISABLE_EXTENSIONS: WebDriverOptionParameter(
        WebDriverOption.DISABLE_EXTENSIONS,
        {
            BrowserType.CHROME: "--disable-extensions",
            BrowserType.EDGE: "--disable-extensions"
        }
    ),
    WebDriverOption.DISABLE_GPU: WebDriverOptionParameter(
        WebDriverOption.DISABLE_GPU,
        {
            BrowserType.CHROME: "--disable-gpu",
            BrowserType.EDGE: "--disable-gpu"
        }
    ),
    WebDriverOption.MAXIMISED: WebDriverOptionParameter(
        WebDriverOption.MAXIMISED,
        {
            BrowserType.CHROME: "--start-maximized",
            BrowserType.EDGE: "--start-maximized"
        }
    ),
    WebDriverOption.PRIVATE: WebDriverOptionParameter(
        WebDriverOption.PRIVATE,
        {
            BrowserType.CHROME: "--incognito",
            BrowserType.EDGE: "--inprivate"
        }
    ),
    WebDriverOption.DISABLE_POPUP_BLOCKING: WebDriverOptionParameter(
        WebDriverOption.DISABLE_POPUP_BLOCKING,
        {
            BrowserType.CHROME: "--disable-popup-blocking",
            BrowserType.EDGE: "--disable-popup-blocking"
        }
    ),
    WebDriverOption.WINDOW_SIZE: WebDriverOptionParameter(
        WebDriverOption.WINDOW_SIZE,
        {
            BrowserType.CHROME: "--window-size",
            BrowserType.EDGE: "--window-size"
        },
        True
    ),
    WebDriverOption.DISABLE_NOTIFICATIONS: WebDriverOptionParameter(
        WebDriverOption.DISABLE_NOTIFICATIONS,
        {
            BrowserType.CHROME: "--disable-notifications",
            BrowserType.EDGE: "--disable-notifications"
        }
    ),
    WebDriverOption.REMOTE_DEBUGGING_PORT: WebDriverOptionParameter(
        WebDriverOption.REMOTE_DEBUGGING_PORT,
        {
            BrowserType.CHROME: "--remote-debugging-port",
            BrowserType.EDGE: "--remote-debugging-port"
        },
        True
    ),
    WebDriverOption.LOG_LEVEL: WebDriverOptionParameter(
        WebDriverOption.LOG_LEVEL,
        {
            BrowserType.CHROME: "--log-level",
            BrowserType.EDGE: "--log-level"
        },
        True
    ),
    WebDriverOption.IGNORE_CERTIFICATE_ERROR: WebDriverOptionParameter(
        WebDriverOption.LOG_LEVEL,
        {
            BrowserType.CHROME: "--ignore-certificate-errors"
        },
        True
    ),
}
