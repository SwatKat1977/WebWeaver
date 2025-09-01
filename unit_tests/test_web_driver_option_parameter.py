import unittest
from unittest.mock import MagicMock
from browser_type import BrowserType
from web_driver_option_parameter import WebDriverOptionParameter


class TestWebDriverOptionParameter(unittest.TestCase):
    def setUp(self):
        # Mock WebDriverOption so we don't depend on enum values
        self.mock_option = MagicMock(name="MockWebDriverOption")

        # Mapping of supported browsers -> option strings
        self.valid_for = {
            BrowserType.CHROME: "--headless=new",
            BrowserType.EDGE: "--headless=edge"
        }

    def test_option_property(self):
        param = WebDriverOptionParameter(self.mock_option, self.valid_for)
        self.assertEqual(param.option, self.mock_option)

    def test_has_parameters_true(self):
        param = WebDriverOptionParameter(self.mock_option, self.valid_for, params=True)
        self.assertTrue(param.has_parameters)

    def test_has_parameters_false(self):
        param = WebDriverOptionParameter(self.mock_option, self.valid_for, params=False)
        self.assertFalse(param.has_parameters)

    def test_is_valid_for_supported_browser(self):
        param = WebDriverOptionParameter(self.mock_option, self.valid_for)
        self.assertTrue(param.is_valid_for(BrowserType.CHROME))

    def test_is_valid_for_unsupported_browser(self):
        param = WebDriverOptionParameter(self.mock_option, self.valid_for)
        self.assertFalse(param.is_valid_for(BrowserType.FIREFOX))

    def test_get_parameter_for_supported_browser(self):
        param = WebDriverOptionParameter(self.mock_option, self.valid_for)
        self.assertEqual(param.get_parameter_for_browser(BrowserType.EDGE), "--headless=edge")

    def test_get_parameter_for_unsupported_browser(self):
        param = WebDriverOptionParameter(self.mock_option, self.valid_for)
        self.assertIsNone(param.get_parameter_for_browser(BrowserType.FIREFOX))
