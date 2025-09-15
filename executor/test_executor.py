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
        #pylint: disable=missing-function-docstring, too-many-locals
        sequential_tasks, parallel_tasks, class_fixtures = self.__collect_from_suite(suite)

        # run before_class hooks
        for hooks in class_fixtures.values():
            for before in hooks["before"]:
                before()

        results = {}

        if parallel_tasks:
            with ThreadPoolExecutor(max_workers=self._max_workers) as executor:
                futures = self.__submit_tasks(executor, sequential_tasks, parallel_tasks)
                results = self.__gather_results(futures)
        else:
            # pure sequential execution (no pool)
            for (name, task, tr, listeners, bm, am) in sequential_tasks:
                out = self.__run_task(task, tr, listeners, bm, am, lock=None)
                if isinstance(out, dict):
                    results.update(out)  # <- flatten wrappers into methods
                elif isinstance(out, TestResult):
                    results[name] = out

        # run after_class hooks
        for hooks in class_fixtures.values():
            for after in hooks["after"]:
                after()

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
        # pylint: disable=too-many-locals

        cls_name = class_conf["name"]
        methods_conf = class_conf.get("methods", {"include": [], "exclude": []})
        cls = self._resolve_class(cls_name)
        obj = cls()

        # listeners attached to the class (used only for method tasks)
        method_listeners = getattr(cls, "__listeners__", [])

        all_methods = [
            attr for attr in dir(obj)
            if callable(getattr(obj, attr)) and getattr(getattr(obj, attr), "is_test", False)
        ]
        selected = self._filter_methods(all_methods, methods_conf)

        # Only collect class-level hooks if at least one enabled test exists
        enabled_methods = [
            m for m in selected if getattr(getattr(obj, m), "enabled", True)
        ]

        if enabled_methods:
            before_class_methods = [
                getattr(obj, m) for m in dir(obj)
                if callable(getattr(obj, m)) and getattr(getattr(obj, m), "is_before_class", False)
            ]
            after_class_methods = [
                getattr(obj, m) for m in dir(obj)
                if callable(getattr(obj, m)) and getattr(getattr(obj, m), "is_after_class", False)
            ]
        else:
            before_class_methods = []
            after_class_methods = []

        before_method_methods = [
            getattr(obj, m) for m in dir(obj)
            if callable(getattr(obj, m)) and getattr(getattr(obj, m), "is_before_method", False)
        ]
        after_method_methods = [
            getattr(obj, m) for m in dir(obj)
            if callable(getattr(obj, m)) and getattr(getattr(obj, m), "is_after_method", False)
        ]

        sequential, parallel = [], []

        if test_parallel == "methods":
            # each method is its own parallel task
            for method_name in selected:
                method = getattr(obj, method_name)
                task_name = f"{cls_name}.{method_name}"
                results_obj = TestResult(method_name, cls_name)
                task = functools.partial(method)
                parallel.append((task_name, task, results_obj, method_listeners,
                                 before_method_methods, after_method_methods))
        else:
            # class wrapper: run methods sequentially INSIDE; return dict of per-method results
            def class_task():
                results = {}
                ran = set()
                try:
                    for method_name in selected:
                        method = getattr(obj, method_name)
                        mtr = TestResult(method_name, cls_name)
                        task = functools.partial(method)
                        res = self.__run_task(task, mtr, method_listeners,
                                              before_method_methods, after_method_methods)
                        results[f"{cls_name}.{method_name}"] = res
                        ran.add(method_name)

                except Exception as ex:
                    # mark remaining methods as SKIPPED if wrapper bombs
                    for method_name in selected:
                        if method_name in ran:
                            continue
                        tr = TestResult(method_name, cls_name)
                        tr.status = TestStatus.SKIPPED
                        tr.caught_exception = ex
                        results[f"{cls_name}.{method_name}"] = tr
                return results

            task_name = f"{cls_name}.__class_wrapper__"
            dummy = TestResult("__class_wrapper__", cls_name)
            task = functools.partial(class_task)

            if test_parallel == "classes":
                parallel.append((task_name, task, dummy, [], [], []))
            else:
                sequential.append((task_name, task, dummy, [], [], []))

        return sequential, parallel, before_class_methods, after_class_methods

    def __collect_from_suite(self, suite: dict):
        sequential_tasks = []
        parallel_tasks = []
        class_fixtures = {}

        suite_conf = suite["suite"]

        for suite_test in suite["tests"]:
            test_parallel = suite_test.get("parallel", suite_conf.get(
                "parallel", "none"))

            if test_parallel == "tests":
                # Wrap whole <test>: run its classes sequentially INSIDE the
                # wrapper, but return a dict of per-method TestResults only.
                def test_block(test=suite_test):
                    results = {}
                    try:
                        for class_conf in test["classes"]:
                            (seq, par, before_class, after_class) = \
                                self._collect_tasks_for_class(class_conf,
                                                              "none")

                            class_name = class_conf["name"]
                            class_fixtures[class_name] = {"before": before_class,
                                                          "after": after_class}

                            # seq here are wrapper tasks returning dicts of method results
                            for (_name, task, result, _listeners, bm, am) in seq:
                                res = self.__run_task(task, result, [], bm, am)
                                # res is a dict of { "Class.method": TestResult }
                                if isinstance(res, dict):
                                    results.update(res)
                                else:
                                    # Safety: in case a method slipped through
                                    results[_name] = res

                    except Exception as ex:
                        # If entire <test> crashes, mark all its methods as SKIPPED
                        for class_conf in test["classes"]:
                            cls_name = class_conf["name"]
                            cls = self._resolve_class(cls_name)
                            obj = cls()
                            all_methods = [attr for attr in dir(obj)
                                           if callable(getattr(obj, attr))
                                           and getattr(getattr(obj, attr),
                                                       "is_test", False)]
                            selected = self._filter_methods(
                                all_methods, class_conf.get("methods",
                                                            {"include": [],
                                                             "exclude": []}))
                            for m in selected:
                                tr = TestResult(m, cls_name)
                                tr.status = TestStatus.SKIPPED
                                tr.caught_exception = ex
                                results[f"{cls_name}.{m}"] = tr

                    return results

                test_name = suite_test.get("name", "UnnamedTest")
                dummy_result = TestResult("__test_wrapper__", test_name)
                parallel_tasks.append((test_name,
                                       test_block,
                                       dummy_result,
                                       [],
                                       [],
                                       []))

            else:
                for class_conf in suite_test["classes"]:
                    (seq, par, before_class, after_class) = \
                        self._collect_tasks_for_class(class_conf, test_parallel)

                    class_name = class_conf["name"]
                    class_fixtures[class_name] = {"before": before_class, "after": after_class}

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
        results = {}
        for future in as_completed(futures):
            name = futures[future]  # wrapper name not used if result is dict
            result = future.result()
            if isinstance(result, dict):
                results.update(result)  # <- only method entries
            elif isinstance(result, TestResult):
                results[name] = result  # <- method tasks only
        return results

    def __run_task(self, task, test_result: TestResult,
                   listeners: list = None,
                   before_methods=None, after_methods=None,
                   lock: threading.Lock = None):
        before_methods = before_methods or []
        after_methods = after_methods or []
        listeners = listeners or []

        def execute():
            test_result.start_milliseconds = int(time.time() * 1000)

            # Peek: is this test enabled?
            is_enabled = True
            if isinstance(task, functools.partial):
                func = getattr(task, "func", None)
                if func is not None:
                    is_enabled = getattr(func, "enabled", True)

            # Only run before_methods if enabled
            if is_enabled:
                for bm in before_methods:
                    bm()

            try:
                result = task()

                if isinstance(result, dict):
                    return result
                if isinstance(result, TestResult):
                    return result
                if isinstance(result, tuple) and len(result) == 2:
                    status, ex = result
                    test_result.status = status
                    test_result.caught_exception = ex
                    return test_result

                test_result.status = TestStatus.SUCCESS
                return test_result

            except Exception as ex:
                test_result.status = TestStatus.FAILURE
                test_result.caught_exception = ex
                return test_result

            finally:
                # Only run after_methods if not skipped
                if test_result.status != TestStatus.SKIPPED:
                    for am in after_methods:
                        try:
                            am()
                        except Exception as ex:
                            self._logger.warning(
                                "Exception in after_method fixture: %s", ex)

                for listener in listeners:
                    if test_result.status is TestStatus.SUCCESS:
                        listener.on_test_success(test_result)
                    elif test_result.status is TestStatus.FAILURE:
                        listener.on_test_failure(test_result)
                    elif test_result.status is TestStatus.SKIPPED:
                        listener.on_test_skipped(test_result)

                test_result.end_milliseconds = int(time.time() * 1000)

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
