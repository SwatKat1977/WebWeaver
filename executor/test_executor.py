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
from test_listener import TestListener
from test_result import TestResult
from test_status import TestStatus


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
        Orchestrates the collection, execution, and result gathering for tests.

        Args:
            test_classes (list[type]): List of test class types.

        Returns:
            dict: Mapping of task name -> TestResult.
        """
        sequential_tasks, parallel_tasks = self.__collect_tasks(test_classes)

        with ThreadPoolExecutor(max_workers=self._max_workers) as executor:
            futures = self.__submit_tasks(executor, sequential_tasks, parallel_tasks)
            results = self.__gather_results(futures)

        return results

    def distribute_results_to_listener(self,
                                       results: dict,
                                       listener: TestListener = None):
        listener: TestListener = listener if listener is not None \
            else TestListener()

        for name, result in results.items():
            self._logger.debug(f"{name} = {result} STATUS: {result.status}")

            if result.status is TestStatus.FAILURE:
                listener.on_test_failure(result)

            elif result.status is TestStatus.SKIPPED:
                listener.on_test_skipped(result)

            elif result.status is TestStatus.SUCCESS:
                listener.on_test_success(result)

    def __collect_tasks(self, test_classes):
        """
        Collects sequential and parallel test tasks from test classes.

        Args:
            test_classes (list[type]): List of test class types.

        Returns:
            tuple[list, list]: (sequential_tasks, parallel_tasks)
        """
        sequential_tasks = []
        parallel_tasks = []

        for cls in test_classes:
            obj = cls()
            for attr_name in dir(obj):
                method = getattr(obj, attr_name)
                if callable(method) and getattr(method, "is_test", False):
                    task_name = f"{cls.__name__}.{attr_name}"
                    results_obj = TestResult(attr_name, cls.__name__)

                    task = functools.partial(method)
                    if getattr(method, "run_in_parallel", False):
                        parallel_tasks.append((task_name, task, results_obj))
                    else:
                        sequential_tasks.append((task_name, task, results_obj))

        return sequential_tasks, parallel_tasks

    def __submit_tasks(self, executor, sequential_tasks, parallel_tasks):
        """
        Submits sequential and parallel tasks to the executor.

        Args:
            executor (ThreadPoolExecutor): Executor for running tasks.
            sequential_tasks (list): List of sequential task tuples.
            parallel_tasks (list): List of parallel task tuples.

        Returns:
            dict: Mapping of Future -> task name.
        """
        futures = {}
        sequential_lock = threading.Lock()

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

        return futures

    def __gather_results(self, futures):
        """
        Waits for all submitted tasks to complete and collects results.

        Args:
            futures (dict): Mapping of Future -> task name.

        Returns:
            dict: Mapping of task name -> TestResult.
        """
        results = {}
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
            mode: str = "SEQUENTIAL" if lock else "PARALLEL"
            self._logger.debug("{%s} %s.%s started at %d",
                               mode,
                               test_result.method_name,
                               test_result.test_class,
                               test_result.start_milliseconds)
            result = task()
            test_result.end_milliseconds = int(time.time() * 1000)
            self._logger.debug("{%s} %s.%s ended at %d",
                               mode,
                               test_result.method_name,
                               test_result.test_class,
                               test_result.end_milliseconds)

            test_result_status, caught_exception = result
            test_result.status = test_result_status
            test_result.caught_exception = caught_exception
            print((f"[DEBUG] {mode} {test_result.method_name}."
                   f"{test_result.test_class} | "
                   f"Status={test_result.status}, "
                   f"caught_except={test_result.caught_exception}"))
            return test_result

        if lock:
            with lock:
                return execute()

        return execute()
