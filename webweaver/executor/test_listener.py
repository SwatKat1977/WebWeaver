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
from webweaver.executor.test_result import TestResult


class TestListener:
    """
    Listener interface for receiving notifications about test execution events.
    """

    def on_test_start(self, result: TestResult) -> None:
        """ Called immediately before a test method begins execution."""

    def on_test_success(self, result: TestResult) -> None:
        """ Called when a test method finishes successfully without raising
            errors. """

    def on_test_failure(self, result: TestResult) -> None:
        """ Called when a test method fails due to an exception or assertion
            error. """

    def on_test_skipped(self, result: TestResult) -> None:
        """ Called when a test method is skipped (disabled or dependency
            failure). """
