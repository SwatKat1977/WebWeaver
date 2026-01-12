from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver import Edge, EdgeOptions
from selenium.webdriver import Firefox, FirefoxOptions, FirefoxProfile
from browsing.browser_type import BrowserType
from browsing.studio_browser import StudioBrowser
from browsing.web_driver_option_target import WebDriverOptionTarget
from browsing.web_driver_option_parameters import WebDriverOptionParameters
from browser_launch_options import BrowserLaunchOptions
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
            _apply_binding(binding, value, browser, chrome_options,
                           edge_options, firefox_profile)


def _apply_binding(binding, value, browser, chrome_options, edge_options,
                   firefox_profile):
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
    browser = BrowserType.from_string(solution.selected_browser)
    launch_opts = solution.browser_launch_options

    if browser == BrowserType.CHROME:
        options = ChromeOptions()
        _apply_browser_launch_options(browser, launch_opts, chrome_options=options)
        driver = Chrome(options=options)

    elif browser == BrowserType.EDGE:
        options = EdgeOptions()
        _apply_browser_launch_options(browser, launch_opts, edge_options=options)
        driver = Edge(options=options)

    elif browser == BrowserType.FIREFOX:
        options = FirefoxOptions()
        profile = FirefoxProfile()
        _apply_browser_launch_options(browser, launch_opts, firefox_profile=profile)
        driver = Firefox(options=options, firefox_profile=profile)

    else:
        raise ValueError(f"Unsupported browser: {browser}")

    return StudioBrowser(browser, driver)
