"""
This source file is part of Web Weaver
For the latest info, see https://github.com/SwatKat1977/WebWeaver

Copyright 2025-2026 Webweaver Development Team

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
import yaml
from webweaver.executor.executor_exceptions import (
    TestSuiteFileNotFound,
    TestSuiteParseFailed)


def load_suite_file(path: Path) -> dict:
    """
    Load a suite file from disk and parse it as JSON or YAML.
    """

    if not path.exists():
        raise TestSuiteFileNotFound(f"Suite file '{path}' not found.")

    # Parse file depending on extension
    try:
        if path.suffix.lower() == ".json":
            with path.open("r", encoding="utf-8") as f:
                return json.load(f)

        elif path.suffix.lower() in (".yaml", ".yml"):
            with path.open("r", encoding="utf-8") as f:
                return yaml.safe_load(f)

        raise TestSuiteParseFailed(
            f"Unsupported file format for '{path}'. "
            "Use .json or .yaml")

    except json.JSONDecodeError as ex:
        raise TestSuiteParseFailed(
            f"Invalid JSON in suite file '{path}': {ex.msg} "
            f"(line {ex.lineno}, column {ex.colno})") from ex

    except yaml.YAMLError as ex:
        raise TestSuiteParseFailed(
            f"Invalid YAML in suite file '{path}': {ex}") from ex
