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
from browsing.browser_type import BrowserType
from browsing.web_driver_option import WebDriverOption
from browsing.web_driver_option_parameter import WebDriverOptionParameter
from browsing.web_driver_option_binding import WebDriverOptionBinding
from browsing.web_driver_option_target import WebDriverOptionTarget


"""
WebDriverOptionParameters

This mapping defines how high-level, browser-agnostic WebDriverOption values are
translated into concrete, browser-specific Selenium configuration operations.

Each entry in this dictionary describes:

- Which browsers support a given option
- How that option should be applied for each supported browser
- Whether the option accepts an additional parameter (e.g. window size, user agent)

The architecture is intentionally data-driven:

1. The StudioSolution produces a set of generic WebDriverOption values.
2. Each option is looked up in this table.
3. The corresponding WebDriverOptionParameter describes:
   - Whether the option is valid for the selected browser
   - Which bindings should be applied
4. Each binding describes:
   - The target configuration mechanism (argument, Chromium pref, Firefox pref)
   - The concrete key or flag to use

This allows:

- Adding new options without changing application logic
- Supporting new browsers by extending the binding tables
- Supporting multiple bindings per option per browser
- Keeping browser-specific knowledge isolated to this module

Structure:

    WebDriverOption -> WebDriverOptionParameter(
        option,
        {
            BrowserType -> [ WebDriverOptionBinding, ... ]
        },
        has_parameters=bool
    )

Example:

    WebDriverOption.DISABLE_NOTIFICATIONS maps to:
    - A Chromium preference for Chrome, Edge, and Chromium
    - A Firefox profile preference for Firefox

This table is the single source of truth for how abstract launch options are
materialised into real WebDriver configuration.
"""
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
