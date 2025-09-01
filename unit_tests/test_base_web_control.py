import unittest
import logging
from unittest.mock import patch, MagicMock

from selenium.common.exceptions import TimeoutException, \
    NoSuchElementException, StaleElementReferenceException

from base_web_control import BaseWebControl


class TestBaseWebControl(unittest.TestCase):
    def setUp(self):
        # Mock WebDriver with dummy .driver
        self.mock_driver = MagicMock()
        self.mock_driver.driver = MagicMock()

        # Real logger, but to memory
        self.logger = logging.getLogger("test")
        self.logger.setLevel(logging.DEBUG)
        self.control = BaseWebControl(self.mock_driver, self.logger)

    @patch("base_web_control.WebDriverWait")
    def test_find_element_success(self, mock_wait):
        """Covers successful element location."""
        mock_element = MagicMock()
        mock_wait.return_value.until.return_value = mock_element

        result = self.control.find_element_by_id("foo")

        self.assertEqual(result, mock_element)
        self.assertEqual(self.control._element, mock_element)

    @patch("base_web_control.WebDriverWait")
    def test_find_element_timeout(self, mock_wait):
        """Covers TimeoutException path."""
        mock_wait.return_value.until.side_effect = TimeoutException("timeout")

        result = self.control.find_element_by_xpath("//div")

        self.assertIsNone(result)

    @patch("base_web_control.WebDriverWait")
    def test_find_element_no_such_element(self, mock_wait):
        """Covers NoSuchElementException path."""
        mock_wait.return_value.until.side_effect = NoSuchElementException("not found")

        result = self.control.find_element_by_class_name("my-class")

        self.assertIsNone(result)

    @patch("base_web_control.WebDriverWait")
    def test_find_element_stale_then_success(self, mock_wait):
        """Covers stale element once, then success."""
        mock_element = MagicMock()
        mock_wait.return_value.until.side_effect = [
            StaleElementReferenceException(),
            mock_element,
        ]

        result = self.control.find_element_by_css("div.class", retries=2)

        self.assertEqual(result, mock_element)
        self.assertEqual(self.control._element, mock_element)

    @patch("base_web_control.WebDriverWait")
    def test_find_element_stale_then_fail(self, mock_wait):
        """Covers repeated stale elements until failure."""
        mock_wait.return_value.until.side_effect = [
            StaleElementReferenceException(),
            StaleElementReferenceException(),
            StaleElementReferenceException(),
        ]

        result = self.control.find_element_by_id("bad-id", retries=2)

        self.assertIsNone(result)
