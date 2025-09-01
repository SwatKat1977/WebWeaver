import unittest
from unittest.mock import Mock, patch, MagicMock
from selenium.common.exceptions import WebDriverException
from web_driver import WebDriver
from browser_type import BrowserType
from exceptions import (
    PageLoadError,
    InvalidBrowserOptionError,
    BrowserOptionIncompatibleError,
    BrowserOptionMissingParameterError,
)


class TestWebDriver(unittest.TestCase):

    def setUp(self):
        # Patch webdriver_manager installers to avoid downloading real binaries
        patcher_chrome = patch("web_driver.ChromeDriverManager")
        patcher_edge = patch("web_driver.EdgeChromiumDriverManager")
        patcher_firefox = patch("web_driver.GeckoDriverManager")
        self.addCleanup(patcher_chrome.stop)
        self.addCleanup(patcher_edge.stop)
        self.addCleanup(patcher_firefox.stop)

        self.mock_chrome_mgr = patcher_chrome.start()
        self.mock_edge_mgr = patcher_edge.start()
        self.mock_firefox_mgr = patcher_firefox.start()

        self.mock_chrome_mgr.return_value.install.return_value = "chromedriver"
        self.mock_edge_mgr.return_value.install.return_value = "edgedriver"
        self.mock_firefox_mgr.return_value.install.return_value = "geckodriver"

        # Patch selenium webdriver constructors
        patcher_chrome_wd = patch("web_driver.webdriver.Chrome")
        patcher_edge_wd = patch("web_driver.webdriver.Edge")
        patcher_firefox_wd = patch("web_driver.webdriver.Firefox")
        self.addCleanup(patcher_chrome_wd.stop)
        self.addCleanup(patcher_edge_wd.stop)
        self.addCleanup(patcher_firefox_wd.stop)

        self.mock_chrome_wd = patcher_chrome_wd.start()
        self.mock_edge_wd = patcher_edge_wd.start()
        self.mock_firefox_wd = patcher_firefox_wd.start()

        # Patch ChromeOptions / EdgeOptions
        patcher_chrome_opts = patch("web_driver.ChromeOptions")
        patcher_edge_opts = patch("web_driver.EdgeOptions")
        self.addCleanup(patcher_chrome_opts.stop)
        self.addCleanup(patcher_edge_opts.stop)

        self.mock_chrome_opts = patcher_chrome_opts.start()
        self.mock_edge_opts = patcher_edge_opts.start()
        self.mock_chrome_opts.return_value.add_argument = Mock()
        self.mock_edge_opts.return_value.add_argument = Mock()

    def test_init_chrome(self):
        driver = WebDriver(BrowserType.CHROME)
        self.mock_chrome_wd.assert_called_once()
        self.assertIsNotNone(driver.driver)

    def test_init_firefox(self):
        driver = WebDriver(BrowserType.FIREFOX)
        self.mock_firefox_wd.assert_called_once()

    def test_init_edge(self):
        driver = WebDriver(BrowserType.EDGE)
        self.mock_edge_wd.assert_called_once()

    def test_init_invalid_browser(self):
        class FakeBrowser:
            value = "FAKE"

        with self.assertRaises(ValueError):
            WebDriver(FakeBrowser)

    def test_driver_property(self):
        driver = WebDriver(BrowserType.CHROME)
        self.assertIs(driver.driver, self.mock_chrome_wd.return_value)

    def test_open_page_success(self):
        driver = WebDriver(BrowserType.CHROME)
        mock_driver = driver.driver
        mock_driver.get = Mock()
        driver.open_page("http://example.com")
        mock_driver.get.assert_called_once_with("http://example.com")

    def test_open_page_failure(self):
        driver = WebDriver(BrowserType.CHROME)
        mock_driver = driver.driver
        mock_driver.get.side_effect = WebDriverException("boom")
        with self.assertRaises(PageLoadError):
            driver.open_page("http://bad")

    @patch("web_driver.WebDriverOptionParameters", new_callable=dict)
    def test_parse_options_none_parameters(self, mock_params):
        driver = WebDriver(BrowserType.CHROME)
        result = driver._WebDriver__parse_options(None, BrowserType.CHROME)
        self.assertIsNone(result)

    @patch("web_driver.WebDriverOptionParameters")
    def test_parse_options_valid_parameter_chrome(self, mock_params):
        mock_entry = Mock()
        mock_entry.is_valid_for.return_value = True
        mock_entry.has_parameters = True
        mock_entry.get_parameter_for_browser.return_value = "--foo"
        mock_params.__getitem__.return_value = mock_entry
        mock_params.__contains__.return_value = True

        driver = WebDriver(BrowserType.CHROME)
        opts = driver._WebDriver__parse_options([("TEST_PARAM", "bar")], BrowserType.CHROME)
        self.mock_chrome_opts.return_value.add_argument.assert_called_with("--foo=bar")
        self.assertIsNotNone(opts)

    @patch("web_driver.WebDriverOptionParameters")
    def test_parse_options_valid_parameter_edge(self, mock_params):
        mock_entry = Mock()
        mock_entry.is_valid_for.return_value = True
        mock_entry.has_parameters = True
        mock_entry.get_parameter_for_browser.return_value = "--foo"
        mock_params.__getitem__.return_value = mock_entry
        mock_params.__contains__.return_value = True

        driver = WebDriver(BrowserType.EDGE)
        opts = driver._WebDriver__parse_options([("TEST_PARAM", "bar")], BrowserType.EDGE)
        self.mock_edge_opts.return_value.add_argument.assert_called_with("--foo=bar")
        self.assertIsNotNone(opts)

    @patch("web_driver.WebDriverOptionParameters")
    def test_parse_options_valid_parameter_firefox(self, mock_params):
        mock_entry = Mock()
        mock_entry.is_valid_for.return_value = True
        mock_entry.has_parameters = True
        mock_entry.get_parameter_for_browser.return_value = "--foo"
        mock_params.__getitem__.return_value = mock_entry
        mock_params.__contains__.return_value = True

        driver = WebDriver(BrowserType.FIREFOX)
        opts = driver._WebDriver__parse_options([("TEST_PARAM", "bar")], BrowserType.FIREFOX)
        self.assertIsNone(opts)

    @patch("web_driver.WebDriverOptionParameters")
    def test_parse_options_valid_parameter_unknown_browser(self, mock_params):
        mock_entry = Mock()
        mock_entry.is_valid_for.return_value = True
        mock_entry.has_parameters = True
        mock_entry.get_parameter_for_browser.return_value = "--foo"
        mock_params.__getitem__.return_value = mock_entry
        mock_params.__contains__.return_value = True

        driver = WebDriver(BrowserType.FIREFOX)
        opts = driver._WebDriver__parse_options([("TEST_PARAM", "bar")], "InvalidBrowserType")
        self.assertIsNone(opts)

    @patch("web_driver.WebDriverOptionParameters")
    def test_parse_options_invalid_parameter(self, mock_params):
        mock_params.__contains__.return_value = False
        driver = WebDriver(BrowserType.CHROME)
        with self.assertRaises(InvalidBrowserOptionError):
            driver._WebDriver__parse_options([("BAD_PARAM",)], BrowserType.CHROME)

    @patch("web_driver.WebDriverOptionParameters")
    def test_parse_options_incompatible_parameter(self, mock_params):
        mock_entry = Mock()
        mock_entry.is_valid_for.return_value = False
        mock_params.__getitem__.return_value = mock_entry
        mock_params.__contains__.return_value = True

        driver = WebDriver(BrowserType.CHROME)
        with self.assertRaises(BrowserOptionIncompatibleError):
            driver._WebDriver__parse_options([("BAD_PARAM",)], BrowserType.CHROME)

    @patch("web_driver.WebDriverOptionParameters")
    def test_parse_options_missing_required_parameter(self, mock_params):
        mock_entry = Mock()
        mock_entry.is_valid_for.return_value = True
        mock_entry.has_parameters = True
        mock_entry.get_parameter_for_browser.return_value = "--foo"
        mock_params.__getitem__.return_value = mock_entry
        mock_params.__contains__.return_value = True

        driver = WebDriver(BrowserType.CHROME)
        with self.assertRaises(BrowserOptionMissingParameterError):
            driver._WebDriver__parse_options([("TEST_PARAM",)], BrowserType.CHROME)

    @patch("web_driver.WebDriverOptionParameters")
    def test_parse_options_no_parameters_needed(self, mock_params):
        mock_entry = Mock()
        mock_entry.is_valid_for.return_value = True
        mock_entry.has_parameters = False
        mock_entry.get_parameter_for_browser.return_value = "--flag"
        mock_params.__getitem__.return_value = mock_entry
        mock_params.__contains__.return_value = True

        driver = WebDriver(BrowserType.CHROME)
        opts = driver._WebDriver__parse_options([("FLAG_PARAM",)], BrowserType.CHROME)
        self.mock_chrome_opts.return_value.add_argument.assert_called_with("--flag")
        self.assertIsNotNone(opts)
