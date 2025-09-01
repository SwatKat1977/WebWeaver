import unittest
from unittest.mock import Mock, patch
from selenium.common.exceptions import WebDriverException

from radio_button_control import RadioButtonControl


class TestRadioButtonControl(unittest.TestCase):

    def setUp(self):
        # Create a mock element and logger for reuse
        self.mock_driver = Mock()
        self.mock_element = Mock()
        self.mock_logger = Mock()

    def test_select_success(self):
        """Should return True when element.click() succeeds."""
        self.mock_element.click.return_value = None
        control = RadioButtonControl(self.mock_driver, self.mock_logger)
        control._element = self.mock_element
        control._logger = self.mock_logger

        result = control.select()

        self.assertTrue(result)
        self.mock_element.click.assert_called_once()
        self.mock_logger.error.assert_not_called()

    def test_select_failure_with_exception(self):
        """Should return False and log error when click() raises WebDriverException."""
        self.mock_element.click.side_effect = WebDriverException("click failed")
        control = RadioButtonControl(self.mock_driver, self.mock_logger)
        control._element = self.mock_element
        control._logger = self.mock_logger

        result = control.select()

        self.assertFalse(result)
        self.mock_logger.error.assert_called_once()
        self.mock_element.click.assert_called_once()

    def test_select_no_element(self):
        """Should return False when _element is None."""
        control = RadioButtonControl(self.mock_driver, self.mock_logger)
        control._element = None
        control._logger = self.mock_logger

        result = control.select()

        self.assertFalse(result)
        self.mock_logger.error.assert_not_called()

    def test_is_selected_true(self):
        """Should return True when element.is_selected() returns True."""
        self.mock_element.is_selected.return_value = True
        control = RadioButtonControl(self.mock_driver, self.mock_logger)
        control._element = self.mock_element

        result = control.is_selected()

        self.assertTrue(result)
        self.mock_element.is_selected.assert_called_once()

    def test_is_selected_false(self):
        """Should return False when element.is_selected() returns False."""
        self.mock_element.is_selected.return_value = False
        control = RadioButtonControl(self.mock_driver, self.mock_logger)
        control._element = self.mock_element

        result = control.is_selected()

        self.assertFalse(result)
        self.mock_element.is_selected.assert_called_once()

    def test_is_selected_no_element(self):
        """Should return False when _element is None."""
        control = RadioButtonControl(self.mock_driver, self.mock_logger)
        control._element = None

        result = control.is_selected()

        self.assertFalse(result)

