import json
import os
import tempfile
import unittest
import yaml

from executor_exceptions import *
from suite_parser import SuiteParser

class TestSuiteParser(unittest.TestCase):
    def setUp(self):
        # Create minimal valid schema for testing
        self.schema = {
            "type": "object",
            "properties": {
                "suite": {"type": "object"},
                "tests": {"type": "array"}
            },
            "required": ["suite", "tests"]
        }

        # Write schema to a temp file (text mode)
        self.schema_file = tempfile.NamedTemporaryFile(delete=False, suffix=".json", mode="w", encoding="utf-8")
        json.dump(self.schema, self.schema_file)
        self.schema_file.close()

        # Minimal valid suite file
        self.suite_data = {
            "suite": {},
            "tests": [{"classes": ["DummyClass"]}]
        }
        self.suite_file = tempfile.NamedTemporaryFile(delete=False, suffix=".json", mode="w", encoding="utf-8")
        json.dump(self.suite_data, self.suite_file)
        self.suite_file.close()

    def tearDown(self):
        os.unlink(self.schema_file.name)
        os.unlink(self.suite_file.name)

    def test_init_loads_schema_successfully(self):
        parser = SuiteParser(self.schema_file.name)  # use full path
        self.assertIsInstance(parser._schema, dict)
        self.assertEqual(parser._schema, self.schema)

    def test_schema_file_not_found(self):
        # Provide a path that does not exist
        non_existent_path = "non_existent_schema.json"
        with self.assertRaises(TestSuiteSchemaFileNotFound) as context:
            SuiteParser(non_existent_path)
        self.assertIn("not found", str(context.exception))

    def test_schema_invalid_json(self):
        # Create a temporary file with invalid JSON
        bad_schema_file = tempfile.NamedTemporaryFile(delete=False, suffix=".json", mode="w", encoding="utf-8")
        bad_schema_file.write("{ invalid json }")  # invalid JSON
        bad_schema_file.close()

        with self.assertRaises(TestSuiteSchemaParseFailed) as context:
            SuiteParser(bad_schema_file.name)
        self.assertIn("Invalid JSON", str(context.exception))

        os.unlink(bad_schema_file.name)

    def test_load_suite_file_not_found(self):
        parser = SuiteParser(self.schema_file.name)
        with self.assertRaises(TestSuiteFileNotFound) as context:
            parser.load_suite("non_existent_suite.json")
        self.assertIn("not found", str(context.exception))

    def test_load_suite_unsupported_file_format(self):
        parser = SuiteParser(self.schema_file.name)
        # Create a temp file with unsupported extension
        unsupported_file = tempfile.NamedTemporaryFile(delete=False, suffix=".txt", mode="w", encoding="utf-8")
        unsupported_file.write("some content")
        unsupported_file.close()

        with self.assertRaises(TestSuiteParseFailed) as context:
            parser.load_suite(unsupported_file.name)
        self.assertIn("Unsupported file format", str(context.exception))

        os.unlink(unsupported_file.name)

    def test_load_suite_normalises_defaults_and_classes(self):
        parser = SuiteParser(self.schema_file.name)  # use full path
        result = parser.load_suite(self.suite_file.name)

        # Suite defaults
        self.assertEqual(result["suite"]["parallel"], "none")
        self.assertEqual(result["suite"]["thread_count"], parser.DEFAULT_SUITE_THREAD_COUNT)

        # Test defaults
        test_entry = result["tests"][0]
        self.assertEqual(test_entry["parallel"], "none")
        self.assertEqual(test_entry["thread_count"], parser.DEFAULT_SUITE_THREAD_COUNT)

        # Class converted from string → dict
        cls_entry = test_entry["classes"][0]
        self.assertIsInstance(cls_entry, dict)
        self.assertIn("name", cls_entry)
        self.assertEqual(cls_entry["methods"]["include"], [])
        self.assertEqual(cls_entry["methods"]["exclude"], [])

    def test_load_suite_yaml_success(self):
        parser = SuiteParser(self.schema_file.name)  # use full path

        yaml_file = tempfile.NamedTemporaryFile(delete=False, suffix=".yaml", mode="w", encoding="utf-8")
        yaml.dump(self.suite_data, yaml_file)
        yaml_file.close()

        result = parser.load_suite(yaml_file.name)
        self.assertIn("suite", result)
        self.assertIn("tests", result)
        os.unlink(yaml_file.name)

    def test_normalise_existing_class_dict_sets_defaults(self):
        parser = SuiteParser(self.schema_file.name)

        suite_data = {
            "suite": {},
            "tests": [
                {
                    "classes": [
                        {
                            "name": "MyClass",
                            "methods": {}  # dict exists but empty
                        }
                    ]
                }
            ]
        }

        result = parser._normalise(suite_data)
        cls_entry = result["tests"][0]["classes"][0]

        # Defaults applied
        self.assertEqual(cls_entry["methods"]["include"], [])
        self.assertEqual(cls_entry["methods"]["exclude"], [])

    def test_normalise_existing_class_dict_else_branch(self):
        parser = SuiteParser(self.schema_file.name)

        # Provide a class that is already a dict without 'methods'
        suite_data = {
            "suite": {},
            "tests": [
                {
                    "classes": [
                        {"name": "AlreadyDictClass"}  # dict without 'methods' key
                    ]
                }
            ]
        }

        # This will execute the else branch
        result = parser._normalise(suite_data)

        cls_entry = result["tests"][0]["classes"][0]

        # The else branch should have added the 'methods' key
        self.assertIn("methods", cls_entry)
        self.assertIsInstance(cls_entry["methods"], dict)
        self.assertEqual(cls_entry["methods"]["include"], [])
        self.assertEqual(cls_entry["methods"]["exclude"], [])

    def test_load_suite_json_decode_error(self):
        parser = SuiteParser(self.schema_file.name)

        # Create a malformed JSON file
        bad_json_file = tempfile.NamedTemporaryFile(delete=False, suffix=".json", mode="w", encoding="utf-8")
        bad_json_file.write("{ invalid json }")  # malformed
        bad_json_file.close()

        with self.assertRaises(TestSuiteParseFailed) as cm:
            parser.load_suite(bad_json_file.name)

        self.assertIn("Invalid JSON in suite file", str(cm.exception))
        os.unlink(bad_json_file.name)

    def test_load_suite_yaml_error(self):
        parser = SuiteParser(self.schema_file.name)

        # Create an invalid YAML file
        bad_yaml_file = tempfile.NamedTemporaryFile(delete=False, suffix=".yaml", mode="w", encoding="utf-8")
        bad_yaml_file.write("this: [ is: invalid yaml")  # malformed YAML
        bad_yaml_file.close()

        with self.assertRaises(TestSuiteParseFailed) as cm:
            parser.load_suite(bad_yaml_file.name)

        self.assertIn("Invalid YAML in suite file", str(cm.exception))
        os.unlink(bad_yaml_file.name)

    def test_load_suite_validation_error(self):
        parser = SuiteParser(self.schema_file.name)

        # Create a suite file that fails validation
        invalid_suite_file = tempfile.NamedTemporaryFile(delete=False, suffix=".json", mode="w", encoding="utf-8")
        json.dump({"invalid": "data"}, invalid_suite_file)
        invalid_suite_file.close()

        with self.assertRaises(ValueError) as cm:
            parser.load_suite(invalid_suite_file.name)

        self.assertIn("Suite validation error", str(cm.exception))
        os.unlink(invalid_suite_file.name)
