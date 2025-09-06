import json
import os
import yaml
from jsonschema import validate, ValidationError
from executor_exceptions import (BaseExecutorException,
                                 TestSuiteSchemaFileNotFound,
                                 TestSuiteSchemaParseFailed)


class SuiteParser:
    """
    Loads and validates a test suite definition (JSON or YAML).
    """

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
        if file_path.endswith(".json"):
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

        elif file_path.endswith((".yaml", ".yml")):
            with open(file_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
        else:
            raise ValueError("Unsupported file format. Use .json or .yaml")

        # Validate against schema
        try:
            validate(instance=data, schema=self._schema)
        except ValidationError as e:
            raise ValueError(f"Suite validation error: {e.message}")

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

        suite = parser.load_suite("../suite.json")   # or "suite.yaml"
        print(json.dumps(suite, indent=2))

    except BaseExecutorException as ex:
        print(f"Caught: {ex}")
