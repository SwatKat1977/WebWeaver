"""
This source file is part of Web Weaver
For the latest info, see https://github.com/SwatKat1977/WebWeaver

Copyright 2025-2026 Webweaver Development Team

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
from browser_type import BrowserType
from web_driver_option import WebDriverOption
from web_driver_option_parameter import WebDriverOptionParameter
from web_driver_option_binding import WebDriverOptionBinding
from web_driver_option_target import WebDriverOptionTarget


WebDriverOptionParameters: dict[WebDriverOption, WebDriverOptionParameter] = {

    WebDriverOption.DISABLE_EXTENSIONS:
        WebDriverOptionParameter(
            WebDriverOption.DISABLE_EXTENSIONS,
            {
                BrowserType.CHROME: [
                    WebDriverOptionBinding(WebDriverOptionTarget.ARGUMENT, "--disable-extensions")
                ],
                BrowserType.EDGE: [
                    WebDriverOptionBinding(WebDriverOptionTarget.ARGUMENT, "--disable-extensions")
                ],
            }
        ),

    WebDriverOption.DISABLE_NOTIFICATIONS:
        WebDriverOptionParameter(
            WebDriverOption.DISABLE_NOTIFICATIONS,
            {
                BrowserType.CHROME: [
                    WebDriverOptionBinding(WebDriverOptionTarget.CHROMIUM_PREF,
                                           "profile.default_content_setting_values.notifications")
                ],
                BrowserType.EDGE: [
                    WebDriverOptionBinding(WebDriverOptionTarget.CHROMIUM_PREF,
                                           "profile.default_content_setting_values.notifications")
                ],
                BrowserType.CHROMIUM: [
                    WebDriverOptionBinding(WebDriverOptionTarget.CHROMIUM_PREF,
                                           "profile.default_content_setting_values.notifications")
                ],
                BrowserType.FIREFOX: [
                    WebDriverOptionBinding(WebDriverOptionTarget.FIREFOX_PREF,
                                           "permissions.default.desktop-notification")
                ],
            }
        ),

    WebDriverOption.MAXIMISED:
        WebDriverOptionParameter(
            WebDriverOption.MAXIMISED,
            {
                BrowserType.CHROME: [
                    WebDriverOptionBinding(WebDriverOptionTarget.ARGUMENT, "--start-maximized")
                ],
                BrowserType.EDGE: [
                    WebDriverOptionBinding(WebDriverOptionTarget.ARGUMENT, "--start-maximized")
                ],
            }
        ),

    WebDriverOption.PRIVATE:
        WebDriverOptionParameter(
            WebDriverOption.PRIVATE,
            {
                BrowserType.CHROME: [
                    WebDriverOptionBinding(WebDriverOptionTarget.ARGUMENT, "--incognito")
                ],
                BrowserType.EDGE: [
                    WebDriverOptionBinding(WebDriverOptionTarget.ARGUMENT, "--inprivate")
                ],
            }
        ),

    WebDriverOption.WINDOW_SIZE:
        WebDriverOptionParameter(
            WebDriverOption.WINDOW_SIZE,
            {
                BrowserType.CHROME: [
                    WebDriverOptionBinding(WebDriverOptionTarget.ARGUMENT, "--window-size")
                ],
                BrowserType.EDGE: [
                    WebDriverOptionBinding(WebDriverOptionTarget.ARGUMENT, "--window-size")
                ],
            },
            has_parameters=True
        ),

    WebDriverOption.USER_AGENT:
        WebDriverOptionParameter(
            WebDriverOption.USER_AGENT,
            {
                BrowserType.CHROME: [
                    WebDriverOptionBinding(WebDriverOptionTarget.ARGUMENT, "--user-agent")
                ],
                BrowserType.EDGE: [
                    WebDriverOptionBinding(WebDriverOptionTarget.ARGUMENT, "--user-agent")
                ],
                BrowserType.FIREFOX: [
                    WebDriverOptionBinding(WebDriverOptionTarget.FIREFOX_PREF,
                                           "general.useragent.override")
                ],
            },
            has_parameters=True
        ),
}
