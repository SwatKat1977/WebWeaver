from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver import Edge, EdgeOptions
from selenium.webdriver import Firefox, FirefoxOptions, FirefoxProfile
from browser_type import BrowserType
from web_driver_option_target import WebDriverOptionTarget
from studio_solution import StudioSolution


def _apply_browser_launch_options(
    browser: BrowserType,
    launch_options: BrowserLaunchOptions,
    chrome_options=None,
    edge_options=None,
    firefox_profile=None,
):
    generic_opts = launch_options.to_webdriver_options()

    for opt, value in generic_opts.items():
        param_def = WebDriverOptionParameters.get(opt)
        if not param_def:
            continue

        if not param_def.is_valid_for(browser):
            continue

        bindings = param_def.bindings_for(browser)
        if not bindings:
            continue

        for binding in bindings:
            _apply_binding(binding, value, browser, chrome_options, edge_options, firefox_profile)


def _apply_binding(binding, value, browser, chrome_options, edge_options, firefox_profile):
    if binding.target == WebDriverOptionTarget.ARGUMENT:
        arg = binding.key
        if value is not None:
            arg = f"{arg}={value}"

        if browser in (BrowserType.CHROME, BrowserType.CHROMIUM):
            chrome_options.add_argument(arg)
        elif browser == BrowserType.EDGE:
            edge_options.add_argument(arg)

    elif binding.target == WebDriverOptionTarget.CHROMIUM_PREF:
        prefs = chrome_options.experimental_options.get("prefs", {})
        prefs[binding.key] = value if value is not None else 0
        chrome_options.add_experimental_option("prefs", prefs)

    elif binding.target == WebDriverOptionTarget.FIREFOX_PREF:
        firefox_profile.set_preference(binding.key, value if value is not None else True)


def create_driver_from_solution(solution: StudioSolution):
    browser = solution.selected_browser
    launch_opts = solution.browser_launch_options

    if browser == BrowserType.CHROME:
        options = ChromeOptions()
        _apply_browser_launch_options(browser, launch_opts, chrome_options=options)
        return Chrome(options=options)

    if browser == BrowserType.EDGE:
        options = EdgeOptions()
        _apply_browser_launch_options(browser, launch_opts, edge_options=options)
        return Edge(options=options)

    if browser == BrowserType.FIREFOX:
        options = FirefoxOptions()
        profile = FirefoxProfile()
        _apply_browser_launch_options(browser, launch_opts, firefox_profile=profile)
        return Firefox(options=options, firefox_profile=profile)

    return None

"""
Usage
from webweaver.studio.browser.driver_factory import create_driver_from_solution

driver = create_driver_from_solution(current_solution)

"""