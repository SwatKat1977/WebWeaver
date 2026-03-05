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
from pathlib import Path


class TestSuiteDocument:
    """Represents a test suite document stored on disk.

    This class wraps the filesystem path of the document and the
    JSON-compatible data loaded from it.
    """
    __slots__ = ["_path", "_data"]

    def __init__(self, path: Path, data: dict):
        """Initialise a TestSuiteDocument.

        Args:
            path: Filesystem path to the test suite document.
            data: JSON-compatible dictionary containing the test suite data.
        """
        self._path = path
        self._data = data

    @property
    def path(self) -> Path:
        """Return the filesystem path of this document.

        Returns:
            Path: Path to the file on disk.
        """
        return self._path

    @property
    def data(self) -> dict:
        """Return the raw test suite data.

        This is the full JSON-compatible dictionary loaded from disk.

        Returns:
            dict: Test suite data dictionary.
        """
        return self._data
