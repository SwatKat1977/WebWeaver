from pathlib import Path
import unittest
import tempfile
from test_suite.suite_loader import load_suite_file
from webweaver.executor.executor_exceptions import (
    TestSuiteFileNotFound,
    TestSuiteParseFailed,
)


class TestTestSuiteSuiteLoader(unittest.TestCase):

    def test_file_not_found(self):
        path = Path("this_file_does_not_exist_12345.json")

        with self.assertRaises(TestSuiteFileNotFound):
            load_suite_file(path)

    def test_load_valid_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "suite.json"
            path.write_text('{"a": 1, "b": 2}', encoding="utf-8")

            result = load_suite_file(path)

            self.assertEqual(result, {"a": 1, "b": 2})

    def test_load_invalid_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "suite.json"
            path.write_text('{"a": 1,', encoding="utf-8")  # broken JSON

            with self.assertRaises(TestSuiteParseFailed) as ctx:
                load_suite_file(path)

            self.assertIn("Invalid JSON", str(ctx.exception))

    def test_load_valid_yaml(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "suite.yaml"
            path.write_text(
                """
                a: 1
                b: 2
                """,
                encoding="utf-8",
            )

            result = load_suite_file(path)

            self.assertEqual(result, {"a": 1, "b": 2})

    def test_load_valid_yml_extension(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "suite.yml"
            path.write_text(
                """
                hello: world
                """,
                encoding="utf-8",
            )

            result = load_suite_file(path)

            self.assertEqual(result, {"hello": "world"})

    def test_load_invalid_yaml(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "suite.yaml"
            path.write_text(
                """
                a: 1
                  b: 2
                """,  # invalid indentation
                encoding="utf-8",
            )

            with self.assertRaises(TestSuiteParseFailed) as ctx:
                load_suite_file(path)

            self.assertIn("Invalid YAML", str(ctx.exception))

    def test_unsupported_extension(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "suite.txt"
            path.write_text("hello", encoding="utf-8")

            with self.assertRaises(TestSuiteParseFailed) as ctx:
                load_suite_file(path)

            self.assertIn("Unsupported file format", str(ctx.exception))
