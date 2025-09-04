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

        Sequential tests are executed one at a time using a lock, while
        parallel tests are executed concurrently. Both run at the same time in
        the executor.
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

                    if getattr(method, "run_in_parallel", False):
                        parallel_tasks.append((task_name,
                                               functools.partial(method),
                                               results_obj))
                    else:
                        sequential_tasks.append((task_name,
                                                 functools.partial(method),
                                                 results_obj))

        results = {}

        with ThreadPoolExecutor(max_workers=self._max_workers) as executor:
            sequential_lock = threading.Lock()
            futures = {}

            # Submit all tasks at once
            for name, task, test_result in sequential_tasks:
                futures[executor.submit(self.__run_task,
                                        task,
                                        test_result,
                                        lock=sequential_lock)] = name

            for name, task, test_result in parallel_tasks:
                futures[executor.submit(self.__run_task,
                                        task,
                                        test_result,
                                        lock=None)] = name

            # Wait for all tasks to complete
            for future in as_completed(futures):
                name = futures[future]
                results[name] = future.result()

        return results

    def __run_task(self,
                   task,
                   test_result: TestResult,
                   lock: threading.Lock = None):
        """
        Executes a test method, updating start and end times in TestResult.

        Args:
            task (callable): The test method to execute.
            test_result (TestResult): Object to record start and end times.
            lock (threading.Lock, optional): Lock for sequential execution. Defaults to None.

        Returns:
            Any: Result of the test method.
        """

        def execute():
            test_result.start_milliseconds = int(time.time() * 1000)
            print(f"[DEBUG] Start: {test_result.method_name}::{test_result.test_class} "
                  f"at {test_result.start_milliseconds}")
            result = task()
            test_result.end_milliseconds = int(time.time() * 1000)
            print(f"[DEBUG] End: {test_result.method_name}::{test_result.test_class} "
                  f"at {test_result.end_milliseconds}")
            return result

        if lock:
            with lock:
                return execute()
        else:
            return execute()
