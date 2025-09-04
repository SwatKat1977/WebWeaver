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
import typing
from test_status import TestStatus


class TestResult:
    """
    Represents the outcome of a single test execution, including its
    status, timing information, and identifying details such as the
    method name and test class.

    This class provides structured access to test metadata and results.
    """
    __slots__ = ["_caught_exception",
                 "_end_time",
                 "_method_name",
                 "_start_time",
                 "_status",
                 "_test_class"]

    def __init__(self,
                 method_name: str,
                 test_class: str):
        """
        Initialize a new TestResult instance.

        Parameters
        ----------
        method_name : str
            The name of the test method executed.
        test_class : str
            The fully qualified name of the test class.
        """
        self._caught_exception: typing.Optional[Exception] = None
        self._end_time: int = 0
        self._method_name: str = method_name
        self._status: TestStatus = TestStatus.CREATED
        self._start_time: int = 0
        self._test_class: str = test_class

    @property
    def status(self) -> TestStatus:
        """
        Get the current test status.

        Returns
        -------
        TestStatus
            The status of the test (CREATED, SUCCESS, FAILURE, SKIP).
        """
        return self._status

    @status.setter
    def status(self, status: TestStatus) -> None:
        """
        Update the test status.

        Parameters
        ----------
        status : TestStatus
            The new status to assign.
        """
        self._status = status

    @property
    def start_milliseconds(self) -> int:
        """
        Get the start time of the test execution.

        Returns
        -------
        int
            Start time in milliseconds since epoch.
        """
        return self._start_time

    @start_milliseconds.setter
    def start_milliseconds(self, time_ms: int) -> None:
        self._start_time = time_ms

    @property
    def end_milliseconds(self) -> int:
        """
        Get the end time of the test execution.

        Returns
        -------
        int
            End time in milliseconds since epoch.
        """
        return self._end_time

    @end_milliseconds.setter
    def end_milliseconds(self, milliseconds) -> None:
        """
        Update the end time of the test execution.

        Parameters
        ----------
        milliseconds : int
            End time in milliseconds since epoch.
        """
        self._end_time = milliseconds

    @property
    def method_name(self) -> str:
        """
        Get the name of the test method.

        Returns
        -------
        str
            The method name that was executed.
        """
        return self._method_name

    @property
    def test_class(self) -> str:
        """
        Get the name of the test class.

        Returns
        -------
        str
            The fully qualified class name containing the test method.
        """
        return self._test_class

    @property
    def caught_exception(self) -> str:
        """
        Gets the exception that was caught during the test execution.

        Returns:
            Exception | None: The exception instance if the test raised one,
                              otherwise None.
        """
        return self._caught_exception

    @caught_exception.setter
    def caught_exception(self, exception: Exception) -> str:
        """
        Sets the exception caught during the test execution.

        Args:
            exception (Exception): The exception instance raised by the test.
        """
        self._caught_exception = exception
