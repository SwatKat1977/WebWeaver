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
import os
import yaml
from jsonschema import validate, ValidationError
from executor_exceptions import (BaseExecutorException,
                                 TestSuiteSchemaFileNotFound,
                                 TestSuiteSchemaParseFailed,
                                 TestSuiteFileNotFound,
                                 TestSuiteParseFailed)


class SuiteParser:
    """
    Loads and validates a test suite definition (JSON or YAML).
    """
    # pylint: disable=too-few-public-methods

    def __init__(self, schema_path: str):
        base_dir = os.path.dirname(__file__)
        full_path = os.path.join(base_dir, schema_path)

        try:
            with open(full_path, "r", encoding="utf-8") as f:
                self._schema = json.load(f)

        except FileNotFoundError as ex:
            raise TestSuiteSchemaFileNotFound(
                f"Schema file '{full_path}' not found.") from ex

        except json.JSONDecodeError as ex:
            raise TestSuiteSchemaParseFailed(
                f"Invalid JSON in schema file {full_path}: {ex.msg} "
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
        if not os.path.exists(file_path):
            raise TestSuiteFileNotFound(f"Suite file '{file_path}' not found.")

        # Parse file depending on extension
        try:
            if file_path.endswith(".json"):
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)

            elif file_path.endswith((".yaml", ".yml")):
                with open(file_path, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)

            else:
                raise TestSuiteParseFailed(
                    (f"Unsupported file format for '{file_path}'. "
                      "Use .json or .yaml"))

        except json.JSONDecodeError as ex:
            raise TestSuiteParseFailed(
                f"Invalid JSON in suite file {file_path}: {ex.msg} "
                f"(line {ex.lineno}, column {ex.colno})"
            ) from ex

        except yaml.YAMLError as ex:
            raise TestSuiteParseFailed(
                f"Invalid YAML in suite file {file_path}: {ex}"
            ) from ex

        # Validate against schema
        try:
            validate(instance=data, schema=self._schema)
        except ValidationError as ex:
            raise ValueError(f"Suite validation error: {ex.message}") from ex

        return self._normalise(data)

    def _normalise(self, data: dict) -> dict:
        """
        Normalize the suite configuration, applying defaults.
        """
        suite = data["suite"]
        suite.setdefault("parallel", "none")
        suite.setdefault("thread_count", 1)

        for test in data["tests"]:
            test.setdefault("parallel", suite.get("parallel", "none"))
            test.setdefault("thread_count", suite.get("thread_count", 1))

        return data


if __name__ == "__main__":

    try:
        parser = SuiteParser("suite_schema.json")

        test_suite = parser.load_suite("test_suite.json")   # or "suite.yaml"
        print(json.dumps(test_suite, indent=2))

    except BaseExecutorException as caught_ex:
        print(f"Caught: {caught_ex}")
