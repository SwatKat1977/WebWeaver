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
import fnmatch
import functools
import logging
import threading
import time
from test_listener import TestListener
from test_result import TestResult
from test_status import TestStatus


class TestExecutor:
    """
    Executes test methods defined in a normalized suite dict.

    Attributes:
        _logger (logging.Logger): Logger instance for logging test execution.
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

    def run_tests(self, suite: dict):
        """
        Orchestrates the collection, execution, and result gathering for tests.

        Args:
            suite (dict): Normalized suite dict from SuiteParser.

        Returns:
            dict: Mapping of task name -> TestResult.
        """
        sequential_tasks, parallel_tasks = self.__collect_from_suite(suite)

        with ThreadPoolExecutor(max_workers=self._max_workers) as executor:
            futures = self.__submit_tasks(executor, sequential_tasks, parallel_tasks)
            results = self.__gather_results(futures)

        return results

    def distribute_results_to_listener(self,
                                       results: dict,
                                       listener: TestListener = None):
        """
        Distribute test results to a listener for handling.

        Iterates over the given test results and notifies the listener
        according to each test's status. If no listener is provided, a
        default `TestListener` instance is created.

        - On failure → `listener.on_test_failure(result)` is called.
        - On skipped → `listener.on_test_skipped(result)` is called.
        - On success → `listener.on_test_success(result)` is called.

        Args:
            results (dict): A mapping of test names (str) to result objects.
                            Each result must expose a `status` attribute of type `TestStatus`.
            listener (TestListener, optional): The listener to notify about
                            test outcomes. Defaults to a new `TestListener` instance.

        Returns:
            None
        """
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

    def __collect_from_suite(self, suite: dict):
        """
        Collects sequential and parallel tasks from a suite definition.

        Args:
            suite (dict): Normalized suite dict.

        Returns:
            tuple[list, list]: (sequential_tasks, parallel_tasks)
        """
        sequential_tasks = []
        parallel_tasks = []

        suite_conf = suite["suite"]
        for test in suite["tests"]:
            test_parallel = test.get("parallel", suite_conf.get("parallel", "none"))

            for class_conf in test["classes"]:
                class_name = class_conf["name"]
                methods_conf = class_conf.get("methods", {"include": [], "exclude": []})

                cls = self._resolve_class(class_name)
                obj = cls()

                # Discover test methods
                all_methods = [
                    attr for attr in dir(obj)
                    if callable(getattr(obj, attr)) and
                                getattr(getattr(obj, attr), "is_test", False)
                ]

                # Apply include patterns with wildcards
                include_patterns = methods_conf.get("include", [])
                if include_patterns:
                    selected = [
                        m for m in all_methods
                        if any(fnmatch.fnmatch(m, pat) for pat in include_patterns)
                    ]
                else:
                    selected = list(all_methods)

                # Apply exclude patterns with wildcards
                exclude_patterns = methods_conf.get("exclude", [])
                if exclude_patterns:
                    selected = [
                        m for m in selected
                        if not any(fnmatch.fnmatch(m, pat) for pat in exclude_patterns)
                    ]

                for method_name in selected:
                    method = getattr(obj, method_name)
                    task_name = f"{cls.__name__}.{method_name}"
                    results_obj = TestResult(method_name, cls.__name__)
                    task = functools.partial(method)

                    if test_parallel in ("tests", "classes", "methods"):
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

    def _resolve_class(self, dotted_path: str):
        """
        Import a class by dotted path, e.g. "com.example.tests.LoginTest".
        """
        module_name, class_name = dotted_path.rsplit(".", 1)
        module = __import__(module_name, fromlist=[class_name])
        return getattr(module, class_name)
