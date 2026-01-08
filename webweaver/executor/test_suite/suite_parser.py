"""
This source file is part of Web Weaver
For the latest info, see https://github.com/SwatKat1977/WebWeaver

Copyright 2025 SwatKat1977

    This program is free software : you can redistribute it and /or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.If not, see < https://www.gnu.org/licenses/>.
"""
import json
from pathlib import Path
from jsonschema import validate, ValidationError
from webweaver.executor.executor_exceptions import (
    TestSuiteSchemaFileNotFound,
    TestSuiteSchemaParseFailed)
from webweaver.executor.test_suite.normalisation import normalise_classes
from webweaver.executor.test_suite.suite_loader import load_suite_file


class SuiteParser:
    """
    Loads and validates a test suite definition provided in JSON or YAML
    format.

    This class is responsible for:
      - Parsing test suite definition files.
      - Validating the structure and required fields of the suite.
      - Providing default configuration values when not explicitly defined.

    Attributes:
        DEFAULT_SUITE_THREAD_COUNT (int): The default number of threads allocated
            for running suites if not specified in the definition.
        DEFAULT_TEST_THREAD_COUNT (int): The default number of threads allocated
            for running individual tests if not specified in the definition.
    """
    # pylint: disable=too-few-public-methods

    DEFAULT_SUITE_THREAD_COUNT: int = 10

    DEFAULT_TEST_THREAD_COUNT: int = 10

    def __init__(self, schema_path: str):
        try:
            with open(schema_path, "r", encoding="utf-8") as f:
                self._schema = json.load(f)

        except FileNotFoundError as ex:
            raise TestSuiteSchemaFileNotFound(
                f"Schema file '{schema_path}' not found.") from ex

        except json.JSONDecodeError as ex:
            raise TestSuiteSchemaParseFailed(
                f"Invalid JSON in schema file {schema_path}: {ex.msg} "
                f"(line {ex.lineno}, column {ex.colno})") from ex

    def load_suite(self, file_path: str) -> dict:
        """
        Load and validate the test suite file.

        Args:
            file_path (str): Path to the JSON or YAML suite file.

        Returns:
            dict: Normalized suite configuration.

        Raises:
            ValueError: If validation fails.
        """
        path: Path = Path(file_path)

        data = load_suite_file(path)

        # Validate against schema
        try:
            validate(instance=data, schema=self._schema)
        except ValidationError as ex:
            raise ValueError(f"Suite validation error: {ex.message}") from ex

        return self._normalise(data)

    def _normalise(self, data: dict) -> dict:
        """
        Normalize the suite configuration, applying defaults and merging classes.

        - suite.parallel defaults to "none"
        - suite.thread_count defaults to DEFAULT_SUITE_THREAD_COUNT
        - test.parallel inherits from suite.parallel if missing
        - test.thread_count:
            * if test.parallel == "none": set to 1
            * else: inherit suite.thread_count if missing, or DEFAULT_TEST_THREAD_COUNT
        - classes:
            * strings and dicts merged by 'name'
            * methods.include/exclude default to [] and are deduped (order preserved)
        """
        suite = data["suite"]

        # Suite-level defaults
        suite.setdefault("parallel", "none")
        suite.setdefault("thread_count", self.DEFAULT_SUITE_THREAD_COUNT)

        for test in data["tests"]:
            # Inherit parallel from suite if not specified
            test["parallel"] = test.get("parallel", suite.get("parallel", "none"))

            # Compute thread_count with sensible defaults
            if test["parallel"] == "none":
                # If user explicitly set a non-1 value while parallel is none, coerce to 1
                test["thread_count"] = 1
            else:
                test.setdefault(
                    "thread_count",
                    suite.get("thread_count", self.DEFAULT_TEST_THREAD_COUNT)
                )

            # Normalise the test classes
            test["classes"] = normalise_classes(test["classes"])

        return data
