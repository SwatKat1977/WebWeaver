import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from webweaver.executor.executor_exceptions import (
    TestSuiteSchemaFileNotFound,
    TestSuiteSchemaParseFailed)
from webweaver.executor.test_suite.suite_parser import SuiteParser
from webweaver.executor.test_suite.suite_validator import TestSuiteValidationFailed


class TestTestSuiteSuiteParser(unittest.TestCase):

    def _make_temp_schema(self, content: dict) -> str:
        fd, path = tempfile.mkstemp(suffix=".json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(content, f)
        return path

    def test_init_schema_file_not_found(self):
        with self.assertRaises(TestSuiteSchemaFileNotFound):
            SuiteParser("does_not_exist.json")

    def test_init_schema_invalid_json(self):
        fd, path = tempfile.mkstemp(suffix=".json")
        with open(path, "w", encoding="utf-8") as f:
            f.write("{ not valid json")

        with self.assertRaises(TestSuiteSchemaParseFailed):
            SuiteParser(path)

    @patch("webweaver.executor.test_suite.suite_parser.normalise_suite")
    @patch("webweaver.executor.test_suite.suite_parser.validate_suite")
    @patch("webweaver.executor.test_suite.suite_parser.load_suite_file")
    def test_load_suite_happy_path(
        self,
        mock_load_suite_file,
        mock_validate_suite,
        mock_normalise_suite,
    ):
        schema_path = self._make_temp_schema({"type": "object"})
        parser = SuiteParser(schema_path)

        raw_data = {"raw": "data"}
        normalised_data = {"normalised": "data"}

        mock_load_suite_file.return_value = raw_data
        mock_normalise_suite.return_value = normalised_data

        result = parser.load_suite("dummy_suite.json")

        mock_load_suite_file.assert_called_once()
        mock_validate_suite.assert_called_once_with(raw_data, parser._schema)
        mock_normalise_suite.assert_called_once_with(
            raw_data,
            parser.DEFAULT_SUITE_THREAD_COUNT,
            parser.DEFAULT_TEST_THREAD_COUNT,
        )

        self.assertEqual(result, normalised_data)

    @patch("webweaver.executor.test_suite.suite_parser.validate_suite")
    @patch("webweaver.executor.test_suite.suite_parser.load_suite_file")
    def test_load_suite_validation_failure(
        self,
        mock_load_suite_file,
        mock_validate_suite,
    ):
        schema_path = self._make_temp_schema({"type": "object"})
        parser = SuiteParser(schema_path)

        raw_data = {"raw": "data"}

        mock_load_suite_file.return_value = raw_data
        mock_validate_suite.side_effect = TestSuiteValidationFailed("boom")

        with self.assertRaises(TestSuiteValidationFailed) as ctx:
            parser.load_suite("dummy_suite.json")

        self.assertIn("Suite validation error", str(ctx.exception))
