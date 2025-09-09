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
    # pylint: disable=too-few-public-methods

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
        (sequential_tasks,
         parallel_tasks,
         class_fixtures) = self.__collect_from_suite(suite)

        # --- Run all class-level before_class hooks ---
        for hooks in class_fixtures.values():
            for before_method in hooks["before"]:
                before_method()

        results = {}
        if parallel_tasks:
            # Parallel execution
            with ThreadPoolExecutor(max_workers=self._max_workers) as executor:
                futures = self.__submit_tasks(executor, sequential_tasks, parallel_tasks)
                results = self.__gather_results(futures)
        else:
            # Pure sequential execution (no threadpool at all)
            for (name, task, test_result,
                 listeners, before_methods, after_methods) in sequential_tasks:
                results[name] = self.__run_task(task,
                                                test_result,
                                                listeners,
                                                before_methods,
                                                after_methods,
                                                lock=None)

        # --- Run all class-level after_class hooks ---
        for hooks in class_fixtures.values():
            for after_method in hooks["after"]:
                after_method()

        return results

    def _filter_methods(self, all_methods, methods_conf):
        include_patterns = methods_conf.get("include", [])
        exclude_patterns = methods_conf.get("exclude", [])

        # Apply include patterns
        if include_patterns:
            selected = [m for m in all_methods
                        if any(fnmatch.fnmatch(m, pat)
                               for pat in include_patterns)]
        else:
            selected = list(all_methods)

        # Apply exclude patterns
        if exclude_patterns:
            selected = [m for m in selected
                        if not any(fnmatch.fnmatch(m, pat)
                                   for pat in exclude_patterns)]

        return selected

    def _collect_method_tasks(self, obj, cls_name, selected_methods, test_parallel):
        """Return sequential and parallel tasks for a list of methods of a class."""
        sequential_tasks = []
        parallel_tasks = []

        for method_name in selected_methods:
            method = getattr(obj, method_name)
            task_name = f"{cls_name}.{method_name}"
            results_obj = TestResult(method_name, cls_name)
            task = functools.partial(method)

            if test_parallel in ("tests", "classes", "methods"):
                parallel_tasks.append((task_name, task, results_obj))
            else:
                sequential_tasks.append((task_name, task, results_obj))

        return sequential_tasks, parallel_tasks

    def _collect_tasks_for_class(self, class_conf, test_parallel):
        """Return sequential and parallel task lists for a single class."""
        # pylint: disable=too-many-locals
        cls_name = class_conf["name"]
        methods_conf = class_conf.get("methods", {"include": [], "exclude": []})
        cls = self._resolve_class(cls_name)
        obj = cls()

        # Discover fixture methods
        before_class_methods = [
            getattr(obj, m) for m in dir(obj)
            if callable(getattr(obj, m)) and getattr(getattr(obj, m),
                                                     "is_before_class",
                                                     False)
        ]
        after_class_methods = [
            getattr(obj, m) for m in dir(obj)
            if callable(getattr(obj, m)) and getattr(getattr(obj, m),
                                                     "is_after_class",
                                                     False)
        ]
        before_method_methods = [
            getattr(obj, m) for m in dir(obj)
            if callable(getattr(obj, m)) and getattr(getattr(obj, m),
                                                     "is_before_method",
                                                     False)
        ]
        after_method_methods = [
            getattr(obj, m) for m in dir(obj)
            if callable(getattr(obj, m)) and getattr(getattr(obj, m),
                                                     "is_after_method",
                                                     False)
        ]

        # Get listeners attached by decorator
        listeners = getattr(cls, "__listeners__", [])

        # Discover test methods
        all_methods = [
            attr for attr in dir(obj)
            if callable(getattr(obj, attr)) and getattr(getattr(obj, attr),
                                                        "is_test", False)
        ]

        selected = self._filter_methods(all_methods, methods_conf)

        sequential = []
        parallel = []

        if test_parallel == "methods":
            # Each method is a parallel task
            for method_name in selected:
                method = getattr(obj, method_name)
                task_name = f"{cls_name}.{method_name}"
                results_obj = TestResult(method_name, cls_name)
                task = functools.partial(method)
                parallel.append((task_name, task, results_obj,
                                 listeners, before_method_methods,
                                 after_method_methods))
        else:
            # Treat the whole class as sequential unit
            def class_task():
                # Run all methods in order
                for method_name in selected:
                    method = getattr(obj, method_name)
                    results_obj = TestResult(method_name, cls_name)
                    task = functools.partial(method)
                    self.__run_task(task, results_obj, listeners,
                                    before_method_methods, after_method_methods)
                return TestResult("ALL_METHODS", cls_name)

            task_name = f"{cls_name}.__class_block__"
            results_obj = TestResult("ALL_METHODS", cls_name)
            task = functools.partial(class_task)

            if test_parallel == "classes":
                parallel.append((task_name, task, results_obj, listeners,
                                 [], []))
            else:
                sequential.append((task_name, task, results_obj, listeners,
                                   [], []))

        return sequential, parallel, before_class_methods, after_class_methods

    def __collect_from_suite(self, suite: dict):
        sequential_tasks = []
        parallel_tasks = []
        class_fixtures = {}

        suite_conf = suite["suite"]

        for test in suite["tests"]:
            test_parallel = test.get("parallel", suite_conf.get("parallel", "none"))

            if test_parallel == "tests":
                # Wrap whole test block into a parallel task
                def test_block():
                    for class_conf in test["classes"]:
                        (seq, par, before_class, after_class) = \
                            self._collect_tasks_for_class(class_conf, "none")

                        class_name = class_conf["name"]
                        class_fixtures[class_name] = {"before": before_class,
                                                      "after": after_class}

                        for (name, task, result, listeners, bm, am) in seq:
                            self.__run_task(task, result, listeners, bm, am)

                test_name = test.get("name", "UnnamedTest")
                results_obj = TestResult("ALL_CLASSES", test_name)
                parallel_tasks.append((test_name, test_block, results_obj, [], [], []))

            else:
                for class_conf in test["classes"]:
                    (seq, par, before_class, after_class) = \
                        self._collect_tasks_for_class(class_conf, test_parallel)

                    class_name = class_conf["name"]
                    class_fixtures[class_name] = {"before": before_class,
                                                  "after": after_class}

                    sequential_tasks.extend(seq)
                    parallel_tasks.extend(par)

        return sequential_tasks, parallel_tasks, class_fixtures

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

        for (name, task, test_result,
             listeners, before_methods, after_methods) in sequential_tasks:
            futures[executor.submit(self.__run_task,
                                    task,
                                    test_result,
                                    listeners,
                                    before_methods=before_methods,
                                    after_methods=after_methods,
                                    lock=sequential_lock)] = name

        for (name, task, test_result,
             listeners, before_methods, after_methods) in parallel_tasks:
            futures[executor.submit(self.__run_task,
                                    task,
                                    test_result,
                                    listeners,
                                    before_methods=before_methods,
                                    after_methods=after_methods,
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
                   listeners: list = None,
                   before_methods=None, after_methods=None,
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
        # pylint: disable=too-many-arguments, too-many-positional-arguments
        before_methods = before_methods or []
        after_methods = after_methods or []
        listeners = listeners or []

        def execute():
            # Call before_method hooks
            for before_method in before_methods:
                before_method()

            test_result.start_milliseconds = int(time.time() * 1000)

            for listener in listeners:
                listener.on_test_start(test_result)

            mode: str = "SEQUENTIAL" if lock else "PARALLEL"
            self._logger.debug("{%s} %s.%s started at %d",
                               mode,
                               test_result.method_name,
                               test_result.test_class,
                               test_result.start_milliseconds)
            try:
                result = task()
                test_result_status, caught_exception = result
                test_result.status = test_result_status
                test_result.caught_exception = caught_exception

            # pylint: disable=broad-exception-caught
            except Exception as ex:
                test_result.status = TestStatus.FAILURE
                test_result.caught_exception = ex
                for listener in listeners:
                    listener.on_test_failure(test_result)

            # SystemExit, KeyboardInterrupt, etc. → bubble up
            except BaseException as ex:
                self._logger.warning("Critical exception in %s.%s: %s",
                                     test_result.test_class,
                                     test_result.method_name,
                                     type(ex).__name__)
                raise  # re-raise after logging

            finally:
                # Call after_method hooks
                for after_method in after_methods:
                    try:
                        after_method()

                    except Exception as ex:
                        self._logger.warning(
                            "Exception in after_method fixture: %s", ex)

                # Notify listeners based on final status
                for listener in listeners:
                    if test_result.status is TestStatus.SUCCESS:
                        listener.on_test_success(test_result)

                    elif test_result.status is TestStatus.FAILURE:
                        listener.on_test_failure(test_result)

                    elif test_result.status is TestStatus.SKIPPED:
                        listener.on_test_skipped(test_result)

                test_result.end_milliseconds = int(time.time() * 1000)
                self._logger.debug("{%s} %s.%s ended at %d",
                                   mode,
                                   test_result.method_name,
                                   test_result.test_class,
                                   test_result.end_milliseconds)

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
