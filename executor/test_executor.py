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
from concurrent.futures import ThreadPoolExecutor, as_completed
import functools
import logging
import threading
import time
from test_result import TestResult


class TestExecutor:
    """
    Executes test methods from given test classes either sequentially or in
    parallel.

    Attributes:
        _logger (logging.Logger): Logger instance for logging test execution
                                  info.
        _max_workers (int): Maximum number of worker threads for parallel
                            execution.
    """

    def __init__(self, logger: logging.Logger, max_workers: int = 3):
        """
        Initializes the TestExecutor.

        Args:
            logger (logging.Logger): Parent logger to create a child logger.
            max_workers (int, optional): Maximum number of parallel workers.
                                         Defaults to 3.
        """
        self._logger = logger.getChild(__name__)
        self._max_workers = max_workers

    def run_tests(self, test_classes):
        """
        Collects test methods from the given classes and executes them.

        Sequential tests are executed one at a time, while parallel tests are
        executed concurrently using a ThreadPoolExecutor.

        Args:
            test_classes (list): List of test class types containing test
                                 methods.

        Returns:
            dict: A dictionary mapping "ClassName.method_name" to test results.
        """
        sequential_tasks = []
        parallel_tasks = []

        # Collect tasks
        for cls in test_classes:
            obj = cls()

            for attr_name in dir(obj):
                method = getattr(obj, attr_name)
                if callable(method) and getattr(method, "is_test", False):
                    task_name = f"{cls.__name__}.{attr_name}"
                    results_obj: TestResult = TestResult(attr_name,
                                                         cls.__name__)

                    if method.run_in_parallel:
                        parallel_tasks.append((task_name,
                                               functools.partial(method),
                                               results_obj))
                    else:
                        sequential_tasks.append((task_name,
                                                 functools.partial(method),
                                                 results_obj))

        # Use a single executor for both sequential and parallel tasks
        with ThreadPoolExecutor(max_workers=self._max_workers) as executor:
            # Create a single lock for sequential tasks
            sequential_lock = threading.Lock()

            # Call the helper functions
            sequential_results = self.__run_sequential_tests(sequential_tasks,
                                                             executor,
                                                             sequential_lock)
            parallel_results = self.__run_parallel_tests(parallel_tasks,
                                                         executor)

        return sequential_results | parallel_results

    def __run_sequential_task(self, lock: threading.Lock, task, test_result):
        """
        Executes a single sequential test method under a lock to enforce
        sequential execution.

        Args:
            lock (threading.Lock): Lock to ensure one-at-a-time execution of
                                   sequential tasks.
            task (callable): Test method to execute.
            test_result (TestResult): TestResult object to store start time
                                      and results.

        Returns:
            Any: Result of the executed test method.
        """
        with lock:
            current_time_ms = int(time.time() * 1000)
            test_result.start_milliseconds = current_time_ms
            print(f"[DEBUG] sequential results info: {test_result.method_name}::"
                  f"{test_result.test_class} started {test_result.start_milliseconds}")
            result = task()
            print(f"TAsk result: {result}")
            return result

    def __run_sequential_tests(self,
                               sequential_tasks: list,
                               executor: ThreadPoolExecutor,
                               lock: threading.Lock) -> dict:
        """
        Executes a list of sequential test methods one at a time using the
        provided executor.

        Args:
            sequential_tasks (list): List of tuples containing task name,
                                     task callable, and TestResult object.
            executor (ThreadPoolExecutor): Executor to submit tasks.
            lock (threading.Lock): Lock to enforce sequential execution.

        Returns:
            dict: Dictionary mapping task names to their results.
        """
        results = {}
        futures = {
            executor.submit(self.__run_sequential_task,
                            lock,
                            task,
                            test_result): name
            for name, task, test_result in sequential_tasks
        }

        for future in as_completed(futures):
            name = futures[future]
            results[name] = future.result()

        return results

    def __run_parallel_tests(self,
                             parallel_tasks: list,
                             executor: ThreadPoolExecutor) -> dict:
        """
        Executes a list of parallel test methods concurrently using the
        provided executor.

        Args:
            parallel_tasks (list): List of tuples containing task name, task
                                   callable, and TestResult object.
            executor (ThreadPoolExecutor): Executor to submit tasks.

        Returns:
            dict: Dictionary mapping task names to their results.
        """
        results = {}
        futures = {
            executor.submit(task): name
            for name, task, _ in parallel_tasks
        }

        for future in as_completed(futures):
            name = futures[future]
            results[name] = future.result()

        return results
