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
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver import Edge, EdgeOptions
from selenium.webdriver import Firefox, FirefoxOptions, FirefoxProfile
from browsing.browser_type import BrowserType
from browsing.studio_browser import StudioBrowser
from browsing.web_driver_option_target import WebDriverOptionTarget
from browsing.web_driver_option_parameters import WEB_DRIVER_OPTION_PARAMETERS
from browser_launch_options import BrowserLaunchOptions
from studio_solution import StudioSolution


def _apply_browser_launch_options(
    browser: BrowserType,
    launch_options: BrowserLaunchOptions,
    chrome_options=None,
    edge_options=None,
    firefox_profile=None):
    """
    Apply browser-agnostic launch options to a specific WebDriver configuration.

    This function takes the high-level BrowserLaunchOptions from a StudioSolution,
    converts them into WebDriver-specific settings, and applies them to the appropriate
    browser configuration objects (Chrome, Edge, or Firefox).

    The option application process is driven by WebDriverOptionParameters, which define:
    - Which options are valid for which browsers
    - How each option maps to concrete WebDriver settings (arguments, prefs, etc)

    Only options that are:
    - Known
    - Valid for the selected browser
    - Have at least one binding

    will be applied.

    :param browser: The selected browser type.
    :param launch_options: High-level launch options from the solution.
    :param chrome_options: ChromeOptions instance (for Chrome/Chromium browsers).
    :param edge_options: EdgeOptions instance (for Edge browser).
    :param firefox_profile: FirefoxProfile instance (for Firefox browser).
    """
    generic_opts = launch_options.to_webdriver_options()

    for opt, value in generic_opts.items():
        param_def = WEB_DRIVER_OPTION_PARAMETERS.get(opt)
        if not param_def:
            continue

        if not param_def.is_valid_for(browser):
            continue

        bindings = param_def.bindings_for(browser)
        if not bindings:
            continue

        for binding in bindings:
            _apply_binding(binding, value, browser, chrome_options,
                           edge_options, firefox_profile)


def _apply_binding(binding, value, browser, chrome_options, edge_options,
                   firefox_profile):
    """
    Apply a single resolved WebDriver option binding to the appropriate browser
    configuration object.

    A binding represents a concrete way of applying an abstract launch option, such as:
    - Adding a command-line argument
    - Setting a Chromium preference
    - Setting a Firefox profile preference

    This function resolves which underlying options object to target based on the
    selected browser and safely applies the binding if applicable.

    :param binding: The resolved binding describing how to apply the option.
    :param value: The value associated with the option.
    :param browser: The selected browser type.
    :param chrome_options: ChromeOptions instance (for Chrome/Chromium).
    :param edge_options: EdgeOptions instance (for Edge).
    :param firefox_profile: FirefoxProfile instance (for Firefox).
    """
    # pylint: disable=too-many-arguments, too-many-positional-arguments

    chromium_options = None
    if browser in (BrowserType.CHROME, BrowserType.CHROMIUM):
        chromium_options = chrome_options
    elif browser == BrowserType.EDGE:
        chromium_options = edge_options

    if binding.target == WebDriverOptionTarget.ARGUMENT:
        arg = binding.key
        if value is not None:
            arg = f"{arg}={value}"

        if chromium_options is not None:
            chromium_options.add_argument(arg)

    elif binding.target == WebDriverOptionTarget.CHROMIUM_PREF:
        if chromium_options is None:
            return

        prefs = chromium_options.experimental_options.get("prefs", {})
        prefs[binding.key] = value if value is not None else 0
        chromium_options.add_experimental_option("prefs", prefs)

    elif binding.target == WebDriverOptionTarget.FIREFOX_PREF:
        if firefox_profile is None:
            return
        firefox_profile.set_preference(binding.key,
                                       value if value is not None else True)

def create_driver_from_solution(solution: StudioSolution) -> StudioBrowser:
    """
    Create and configure a StudioBrowser instance from a StudioSolution.

    This function:
    - Determines the target browser from the solution
    - Constructs the appropriate Selenium WebDriver configuration objects
    - Applies all solution-defined launch options
    - Creates the underlying WebDriver instance
    - Wraps it in a StudioBrowser abstraction

    This is the single factory entry point for browser creation in the Studio.

    :param solution: The loaded StudioSolution containing browser and launch settings.
    :return: A fully initialised StudioBrowser instance.
    :raises ValueError: If the selected browser type is not supported.
    """
    browser = BrowserType.from_string(solution.selected_browser)
    launch_opts = solution.browser_launch_options

    if browser == BrowserType.CHROME:
        options = ChromeOptions()

        # Silence Chrome noise
        options.add_argument("--log-level=3")
        options.add_argument("--disable-logging")
        options.add_experimental_option("excludeSwitches", ["enable-logging"])

        _apply_browser_launch_options(browser, launch_opts, chrome_options=options)
        driver = Chrome(options=options)

    elif browser == BrowserType.EDGE:
        options = EdgeOptions()

        # Silence Edge/Chromium noise
        options.add_argument("--log-level=3")
        options.add_argument("--disable-logging")
        options.add_experimental_option("excludeSwitches", ["enable-logging"])

        _apply_browser_launch_options(browser, launch_opts, edge_options=options)
        driver = Edge(options=options)

    elif browser == BrowserType.FIREFOX:
        options = FirefoxOptions()
        profile = FirefoxProfile()
        _apply_browser_launch_options(browser, launch_opts, firefox_profile=profile)
        driver = Firefox(options=options)

    else:
        raise ValueError(f"Unsupported browser: {browser}")

    return StudioBrowser(driver)
