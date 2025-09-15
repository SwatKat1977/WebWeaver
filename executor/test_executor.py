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
from dataclasses import dataclass
import fnmatch
import functools
import logging
import threading
import time
from test_result import TestResult
from test_status import TestStatus


@dataclass
class TaskContext:
    """
    Context container for managing task execution state, lifecycle hooks,
    and optional synchronization.

    Attributes:
        listeners (list | None): A collection of listener objects or callbacks
            that can be notified about task-related events, or None if not set.
        before_methods (list | None): Callables to be executed before the main
            task logic runs, or None if not defined.
        after_methods (list | None): Callables to be executed after the main
            task logic completes, or None if not defined.
        lock (threading.Lock | None): Optional lock for thread-safe access and
            modification of the context, or None if synchronization is not required.
    """
    listeners: list | None = None
    before_methods: list | None = None
    after_methods: list | None = None
    lock: threading.Lock | None = None


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
            for (name, task, test_result, listeners, before_methods,
                 after_methods) in sequential_tasks:
                ctx = TaskContext(
                    listeners=listeners,
                    before_methods=before_methods,
                    after_methods=after_methods,
                    lock=None
                )
                out = self.__run_task(task, test_result, ctx)
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
        """
        Filter a list of method names based on inclusion and exclusion patterns.

        Parameters:
            all_methods (Iterable[str]): The complete set of method names to
            filter.
            methods_conf (dict): A configuration dictionary that may contain:
                - "include" (list[str]): Glob-style patterns to explicitly
                  include. If omitted or empty, all methods are considered
                  initially.
                - "exclude" (list[str]): Glob-style patterns to exclude from the
                  final selection.

        Returns:
            list[str]: The subset of method names that match the inclusion
            patterns (if any are provided) and do not match the exclusion
            patterns.
        """
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
        """
        Collect tasks for the given object's methods and categorize them as
        sequential or parallel based on the test execution mode.

        Parameters:
            obj (object): The instance containing the methods to execute.
            cls_name (str): The class name of the object, used for task naming.
            selected_methods (Iterable[str]): Names of methods to wrap as tasks.
            test_parallel (str): Execution mode indicator. If set to "tests",
                "classes", or "methods", tasks will be marked as parallel;
                otherwise, they will be sequential.

        Returns:
            tuple[list[tuple[str, Callable, TestResult]], list[tuple[str, Callable, TestResult]]]:
                A tuple containing two lists:
                - sequential_tasks: Tasks to run sequentially.
                - parallel_tasks: Tasks to run in parallel.
                Each task is represented as a tuple of
                (task_name, task_callable, TestResult).
        """
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

                        ctx = TaskContext(
                            listeners=method_listeners,
                            before_methods=before_method_methods,
                            after_methods=after_method_methods,
                            lock=None
                        )
                        res = self.__run_task(task, mtr, ctx)
                        results[f"{cls_name}.{method_name}"] = res
                        ran.add(method_name)

                # NOTE: Disabling broad exception here because this is a
                #       user-defined method, and we don't know what exception
                #       could be caught.
                except Exception as ex:  # pylint:  disable=broad-exception-caught
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
        """
        Collect tasks from a test suite configuration and categorize them into
        sequential tasks, parallel tasks, and class-level fixtures.

        This method inspects the suite definition, determines whether tests
        should run sequentially or in parallel (based on suite or test-level
        `parallel` configuration), and prepares callable task wrappers along
        with associated fixtures.

        Parameters:
            suite (dict): A dictionary describing the test suite. Expected keys:
                - "suite" (dict): Suite-level configuration, may contain
                  `"parallel"` to set default parallelism.
                - "tests" (list[dict]): A list of test configurations. Each
                                        test may
                  contain:
                    * "name" (str, optional): The test name.
                    * "parallel" (str, optional): Parallelism mode, overrides
                      the suite-level setting. Accepted values are
                      `"tests"`, `"classes"`, `"methods"`, or `"none"`.
                    * "classes" (list[dict]): Class-level configurations, each
                      with:
                        - "name" (str): Class name.
                        - "methods" (dict, optional): Filtering configuration
                          for selecting test methods with `"include"` /
                          `"exclude"`.

        Returns:
            tuple[
                list[tuple[str, Callable, TestResult, list, list, list]],
                list[tuple[str, Callable, TestResult, list, list, list]],
                dict[str, dict[str, list]]
            ]:
                A tuple containing:
                - sequential_tasks: Tasks to run sequentially.
                - parallel_tasks: Tasks to run in parallel.
                - class_fixtures: A mapping of class names to their fixtures
                  with `"before"` and `"after"` method lists.
        """
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
                            (seq, _, before_class, after_class) = \
                                self._collect_tasks_for_class(class_conf,
                                                              "none")

                            class_name = class_conf["name"]
                            class_fixtures[class_name] = {"before": before_class,
                                                          "after": after_class}

                            # seq here are wrapper tasks returning dicts of method results
                            for (_name, task, result, listeners,
                                 before_methods, after_methods) in seq:
                                ctx = TaskContext(
                                    listeners=listeners,
                                    before_methods=before_methods,
                                    after_methods=after_methods,
                                    lock=None
                                )
                                res = self.__run_task(task, result, ctx)
                                # res is a dict of { "Class.method": TestResult }
                                if isinstance(res, dict):
                                    results.update(res)
                                else:
                                    # Safety: in case a method slipped through
                                    results[_name] = res

                    # NOTE: Disabling broad exception here because this is a
                    #       user-defined method, and we don't know what exception
                    #       could be caught.
                    except Exception as ex:  # pylint:  disable=broad-exception-caught
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
            ctx = TaskContext(
                listeners=listeners,
                before_methods=before_methods,
                after_methods=after_methods,
                lock=sequential_lock
            )
            futures[executor.submit(self.__run_task,
                                    task,
                                    test_result,
                                    ctx)] = name

        for (name, task, test_result,
             listeners, before_methods, after_methods) in parallel_tasks:
            ctx = TaskContext(
                listeners=listeners,
                before_methods=before_methods,
                after_methods=after_methods,
                lock=None
            )
            futures[executor.submit(self.__run_task,
                                    task,
                                    test_result,
                                    ctx)] = name

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
                   ctx: TaskContext = None):
        ctx = ctx or TaskContext()
        before_methods = ctx.before_methods or []
        after_methods = ctx.after_methods or []
        listeners = ctx.listeners or []

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

            # NOTE: Disabling broad exception here because this is a
            #       user-defined method, and we don't know what exception could
            #       be caught.
            except Exception as ex:  # pylint:  disable=broad-exception-caught
                test_result.status = TestStatus.FAILURE
                test_result.caught_exception = ex
                return test_result

            finally:
                # Only run after_methods if not skipped
                if test_result.status != TestStatus.SKIPPED:
                    for am in after_methods:
                        try:
                            am()

                        # NOTE: Disabling broad exception here because this is
                        #       a user-defined method, and we don't know what
                        #       exception could be caught.
                        except Exception as ex:  # pylint:  disable=broad-exception-caught
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

        if ctx.lock:
            with ctx.lock:
                return execute()
        return execute()

    def _resolve_class(self, dotted_path: str):
        """
        Import a class by dotted path, e.g. "com.example.tests.LoginTest".
        """
        module_name, class_name = dotted_path.rsplit(".", 1)
        module = __import__(module_name, fromlist=[class_name])
        return getattr(module, class_name)
