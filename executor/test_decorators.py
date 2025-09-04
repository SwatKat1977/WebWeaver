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
import functools
from executor_exceptions import TestFailure
from test_result import TestResult
from test_status import TestStatus


# === Decorator to mark test methods ===
def test(parallel=False):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # args[0] is usually 'self', so we can get the class name
            cls_name = type(args[0]).__name__ if args else "<UnknownClass>"
            method_name = func.__name__
            print(f"Class: {cls_name} | method: {method_name}")

            try:
                func(*args, **kwargs)
                status = TestStatus.SUCCESS

            except TestFailure as e:
                status = f"FAIL: {e}"  # caught failure raised intentionally

            except Exception as e: # pylint: disable=broad-exception-caught
                status = f"FAIL: {e}"  # caught unexpected exceptions

            """
            class TestResult:

    def __init__(self,
                 status: TestStatus,
                 start_time: int,
                 end_time: int,
                 method_name: str,
                 test_class: str):
            """

            return TestResult(status, 0, 10, method_name, cls_name)
            # Return a tuple (class_name, method_name, status)
            return cls_name, method_name, status

        wrapper.is_test = True
        wrapper.run_in_parallel = parallel
        return wrapper
    return decorator
