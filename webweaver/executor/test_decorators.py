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
import asyncio
import functools
from webweaver.executor.executor_exceptions import TestFailure
from webweaver.executor.test_status import TestStatus

data_providers = {}


def data_provider(name):
    """
    Registers a function as a named data provider.

    A data provider is a function that supplies test data to parameterized
    tests. The decorated function will be stored in the global `data_providers`
    registry under the given name.

    Args:
        name: The name under which to register the data provider.

    Returns:
        A decorator that registers the decorated function as a data provider.
    """
    def wrapper(func):
        data_providers[name] = func
        return func

    return wrapper


# === Decorator to mark test methods ===
def test(provider=None, parallel=False, enabled=True):
    """
    Marks a function as a test case.

    This decorator wraps the function in a test execution harness that:
    - Handles synchronous and asynchronous test functions.
    - Catches test failures and unexpected exceptions.
    - Returns a standardized (TestStatus, exception) tuple.
    - Attaches metadata to the function for the test runner.

    Args:
        provider:
            Optional data provider function or name used to supply test data.
        parallel:
            If True, this test is allowed to run in parallel with others.
        enabled:
            If False, the test will be skipped.

    Returns:
        A decorator that transforms a function into a managed test case.
    """
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            if not enabled:
                return TestStatus.SKIPPED, None

            try:
                result = func(*args, **kwargs)
                if asyncio.iscoroutine(result):
                    await result
                return TestStatus.SUCCESS, None

            except TestFailure as ex:
                return TestStatus.FAILURE, ex

            except Exception as ex:
                return TestStatus.FAILURE, ex

        wrapper.is_test = True
        wrapper.run_in_parallel = parallel
        wrapper.enabled = enabled
        wrapper.data_provider = provider  # store provider function!
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
