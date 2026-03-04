"""
This source file is part of Web Weaver
For the latest info, see https://github.com/SwatKat1977/WebWeaver

Copyright 2025-2026 Webweaver Development Team

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
import json
from pathlib import Path
from webweaver.studio.persistence.test_suite_document import TestSuiteDocument


class TestSuiteLoadError(Exception):
    """Raised when a test suite file cannot be loaded."""


class TestSuiteSaveError(Exception):
    """Raised when a test suite file cannot be saved."""


class TestSuitePersistence:
    """
    Persistence layer for TestSuiteDocument objects.

    Responsible for loading and saving test suite documents to and from disk.
    """

    @staticmethod
    def load_from_disk(suite_file: Path) -> TestSuiteDocument:
        """Load a test suite file from disk.

        Args:
            suite_file: Path to the ``.wwsuite`` file.

        Returns:
            TestSuiteDocument: Loaded test suite document.

        Raises:
            TestSuiteLoadError: If the file cannot be read or parsed.
        """
        try:
            text = suite_file.read_text(encoding="utf-8")
            data = json.loads(text)
            return TestSuiteDocument(suite_file, data)

        except (OSError, json.JSONDecodeError) as ex:
            raise TestSuiteLoadError(
                f"Failed to load test suite: {suite_file}") from ex

    @staticmethod
    def save_to_disk(test_suite: TestSuiteDocument) -> None:
        """Save a test suite document to disk.

        Args:
            test_suite: TestSuiteDocument instance to save.

        Raises:
            TestSuiteSaveError: If the file cannot be written.
        """
        try:
            test_suite.path.write_text(
                json.dumps(test_suite.data, indent=2),
                encoding="utf-8")

        except OSError as ex:
            raise TestSuiteSaveError(
                f"Failed to save test_suite: {test_suite.path}") from ex
