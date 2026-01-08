import unittest
from test_suite.suite_validator import (
    validate_suite, TestSuiteValidationFailed)


class TestTestSuiteSuiteValidator(unittest.TestCase):

    def test_validate_suite_success(self):
        """
        Should not raise when data matches schema.
        """
        schema = {
            "type": "object",
            "properties": {
                "suite": {"type": "object"},
            },
            "required": ["suite"],
        }

        data = {
            "suite": {}
        }

        # Should not raise
        validate_suite(data, schema)

    def test_validate_suite_failure(self):
        """
        Should raise TestSuiteValidationFailed when data does not match schema.
        """
        schema = {
            "type": "object",
            "properties": {
                "suite": {"type": "object"},
            },
            "required": ["suite"],
        }

        data = {
            # Missing "suite"
        }

        with self.assertRaises(TestSuiteValidationFailed) as ctx:
            validate_suite(data, schema)

        # Optional: assert message is not empty
        self.assertTrue(str(ctx.exception))
