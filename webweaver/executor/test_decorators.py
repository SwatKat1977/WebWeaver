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
from test_status import TestStatus


# === Decorator to mark test methods ===
def test(parallel: bool = False,
         enabled: bool = True):
    """
    Decorator to mark a function as a test case.

    This decorator wraps the target function and executes it safely,
    capturing any exceptions raised during execution. It records the
    outcome as either a success or a failure and attaches metadata
    used by the test runner.

    Parameters
    ----------
    parallel : bool, optional
        If True, the test is marked to be run in parallel (default: False).

    Returns
    -------
    decorator : Callable
        A decorator function that can be applied to test functions.

    Notes
    -----
    - The decorated function is wrapped in a try/except block.
    - If the function executes without raising an exception, the status
      will be ``TestStatus.SUCCESS``.
    - If the function raises a ``TestFailure`` or any other exception,
      the status will be ``TestStatus.FAILURE`` and the exception will
      be returned alongside the status.
    - The wrapper attaches two attributes to the decorated function:
        * ``is_test``: Marks the function as a test (True).
        * ``run_in_parallel``: Indicates whether it should run in parallel.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if not enabled:
                # You could introduce a SKIPPED status if you have one,
                # or just return SUCCESS with a note.
                return TestStatus.SKIPPED, None

            caught_exception = None

            try:
                func(*args, **kwargs)
                status = TestStatus.SUCCESS

            except TestFailure as ex:
                caught_exception = ex
                status = TestStatus.FAILURE

            except Exception as ex:  # pylint: disable=broad-exception-caught
                caught_exception = ex
                status = TestStatus.FAILURE

            return status, caught_exception

        wrapper.is_test = True
        wrapper.run_in_parallel = parallel
        wrapper.enabled = enabled
        return wrapper
    return decorator


def listener(*listener_classes):
    """
    Class decorator to attach one or more listener classes to a test class.
    """
    def wrapper(cls):
        setattr(cls, "__listeners__", [lc() for lc in listener_classes])
        return cls
    return wrapper


def before_class(func):
    """ Runs once before any test methods in a class are executed.
        Use it for expensive setup that only needs to happen once (e.g.,
        creating a database connection, starting a server). """
    func.is_before_class = True
    return func


def after_class(func):
    """ Runs once after all test methods in a class are executed.
        Use it for cleanup corresponding to @before_class (closing connections,
        stopping servers, deleting temp files). """
    func.is_after_class = True
    return func


def before_method(func):
    """ Runs before every test method in the class.
        Use it for per-test setup (resetting state, creating fresh objects,
        clearing caches). """
    func.is_before_method = True
    return func


def after_method(func):
    """ Runs after every test method in the class.
        Use it for per-test cleanup (rollback database changes, reset global
        state). """
    func.is_after_method = True
    return func
