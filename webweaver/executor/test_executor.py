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
import inspect
from dataclasses import dataclass
from enum import IntEnum
import fnmatch
import logging
import threading
import time
import typing
from webweaver.executor.test_result import TestResult
from webweaver.executor.test_status import TestStatus
from webweaver.executor.assertions import (
    SoftAssertions, AssertionFailure, AssertionContext)
from webweaver.executor.discovery.class_resolver import resolve_class

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
    listeners: typing.Optional[list] = None
    before_methods: typing.Optional[list] = None
    after_methods: typing.Optional[list] = None
    lock: typing.Optional[threading.Lock] = None


class SequentialTaskIndex(IntEnum):
    """
    Index positions for elements within a sequential task tuple.

    A sequential task is represented as a 6-element tuple:

        (name, task, result, listeners, before_methods, after_methods)

    Attributes:
        NAME (int): Index of the task name (str), typically in the form
            "Class.method".
        TASK (int): Index of the callable to be executed.
        RESULT (int): Index of the TestResult object associated with the task.
        LISTENERS (int): Index of the list of listeners attached to the task.
        BEFORE_METHODS (int): Index of the list of methods to run before the task.
        AFTER_METHODS (int): Index of the list of methods to run after the task.
    """
    NAME = 0
    TASK = 1
    RESULT = 2
    LISTENERS = 3
    BEFORE_METHODS = 4
    AFTER_METHODS = 5


class ClassTaskIndex(IntEnum):
    """
    Index positions for elements within the tuple returned by
    `_collect_tasks_for_class`.

    That tuple has the following structure:

        (sequential_tasks, parallel_tasks, before_classes, after_classes)

    Attributes:
        SEQUENTIAL (int): Index of the list of sequential tasks for the class.
        PARALLEL (int): Index of the list of parallel tasks for the class.
        BEFORE_CLASSES (int): Index of the list of class-level setup
            ("before") methods.
        AFTER_CLASSES (int): Index of the list of class-level teardown
            ("after") methods.
    """
    SEQUENTIAL = 0
    PARALLEL = 1
    BEFORE_CLASS = 2
    AFTER_CLASS = 3


class TestExecutor:
    """
    Executes test methods defined in a normalized suite dict.

    Attributes:
        _logger (logging.Logger): Logger instance for logging test execution.
    """
    # pylint: disable=too-few-public-methods

    def __init__(self, logger: logging.Logger):
        """
        Initializes the TestExecutor.

        Args:
            logger (logging.Logger): Parent logger to create a child logger.
        """
        # Executor logger
        self._logger = logger.getChild("executor")

        # === Ensure a single console handler exists SOMEWHERE ===
        # Prefer using the handler(s) already on the passed-in logger.
        def _ensure_console_handler_on(lgr: logging.Logger) -> None:
            if not lgr.handlers:
                h = logging.StreamHandler()
                h.setFormatter(logging.Formatter(
                    "%(asctime)s [%(levelname)s] %(message)s",
                    "%Y-%m-%d %H:%M:%S",
                ))
                lgr.addHandler(h)

        # If the root has no handlers and the provided logger has none,
        # create a sane default on the provided logger.
        root = logging.getLogger()
        if not root.handlers and not logger.handlers:
            _ensure_console_handler_on(logger)

        # === Make 'webweaver' the sink for all test logs ===
        weaver = logging.getLogger("webweaver")

        # If 'webweaver' has no handlers, borrow the provided logger's handlers.
        if not weaver.handlers:
            for h in logger.handlers:
                if h not in weaver.handlers:
                    weaver.addHandler(h)

        # Keep propagation ON so child loggers bubble to 'webweaver' if needed.
        weaver.propagate = False  # weaver itself owns handlers now
        weaver.setLevel(logger.level or logging.DEBUG)

        # Remove duplicate handlers from executor logger to avoid double output
        for h in list(self._logger.handlers):
            self._logger.removeHandler(h)

        self._logger.debug("Executor logging pipeline initialized. "
                           f"weaver.handlers={len(weaver.handlers)}, "
                           f"root.handlers={len(root.handlers)}, "
                           f"exec.handlers={len(self._logger.handlers)}")

    async def run_tests(self, suite: dict):
        # pylint: disable=too-many-locals
        (sequential_tasks,
         parallel_tasks,
         class_fixtures) = await self.__collect_from_suite(suite)

        # run before_class hooks
        for hooks in class_fixtures.values():
            for before in hooks["before"]:
                result = before()
                if inspect.iscoroutine(result):
                    await result

        results = {}

        # === PARALLEL EXECUTION (async replacement for ThreadPoolExecutor) ===
        if parallel_tasks:
            tasks = []

            for (name, task, test_result, listeners, before_methods, after_methods) in parallel_tasks:
                ctx = TaskContext(
                    listeners=listeners,
                    before_methods=before_methods,
                    after_methods=after_methods,
                    lock=None
                )
                tasks.append(self.__run_task(task, test_result, ctx))

            # Run everything concurrently
            parallel_results = await asyncio.gather(*tasks)

            # Merge results back into dict
            for (name, *_), res in zip(parallel_tasks, parallel_results):
                if isinstance(res, dict):
                    results.update(res)
                else:
                    results[name] = res

        # === SEQUENTIAL EXECUTION ===
        else:
            for (name, task, test_result, listeners, before_methods,
                 after_methods) in sequential_tasks:
                ctx = TaskContext(
                    listeners=listeners,
                    before_methods=before_methods,
                    after_methods=after_methods,
                    lock=None
                )
                out = await self.__run_task(task, test_result, ctx)

                if isinstance(out, dict):
                    results.update(out)  # <- flatten wrappers into methods
                elif isinstance(out, TestResult):
                    results[name] = out

        # run after_class hooks
        for hooks in class_fixtures.values():
            for after in hooks["after"]:
                result = after()
                if inspect.iscoroutine(result):
                    await result

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
            task = method

            if test_parallel in ("tests", "classes", "methods"):
                parallel_tasks.append((task_name, task, results_obj))
            else:
                sequential_tasks.append((task_name, task, results_obj))

        return sequential_tasks, parallel_tasks

    def _create_test_instance(self, class_conf):
        cls_name = class_conf["name"]
        cls = resolve_class(cls_name)
        obj = cls()
        return cls_name, cls, obj

    async def _collect_tasks_for_class(self, class_conf, test_parallel):
        # pylint: disable=too-many-locals

        cls_name, cls, obj = self._create_test_instance(class_conf)
        methods_conf = class_conf.get("methods", {"include": [], "exclude": []})

        # Inject shared test logger into the class instance if not already present
        # Inject shared test logger into the class instance if not already present
        if not hasattr(obj, "logger"):
            obj.logger = logging.getLogger(f"webweaver.{cls_name}")

            # Add a clean formatter with (Class::Method)
            short_cls = cls_name.rsplit(".", 1)[-1]
            for handler in obj.logger.handlers or logging.getLogger("webweaver").handlers:
                handler.setFormatter(logging.Formatter(
                    "%(asctime)s [%(levelname)s] "
                    f"({short_cls}::%(funcName)s) %(message)s",
                    "%Y-%m-%d %H:%M:%S",
                ))

            self._logger.debug(f"Injected logger into test class: {cls_name}")

        # === Inject soft/hard assertion helpers ===

        # Hard assertion context — raises immediately (assert/assume)
        if not hasattr(obj, "assertions"):
            obj.assertions = AssertionContext(obj.logger)

        # Soft assertions collector — records and summarizes later
        if not hasattr(obj, "softly"):
            obj.softly = SoftAssertions(obj.logger)

        # Bind convenience methods for hard assertions
        if not hasattr(obj, "assert_that"):
            obj.assert_that = obj.assertions.assert_that

        if not hasattr(obj, "assume_that"):
            obj.assume_that = obj.assertions.assume_that

        # link assertion context to collector for assume_that()
        obj.assertions.soft_collector = obj.softly

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

        if test_parallel != "classes":
            for method_name in selected:
                method = getattr(obj, method_name)
                provider = getattr(method, "data_provider", None)

                # ---------- CASE 1: Data Provider ----------
                if provider:
                    rows = provider()
                    if inspect.iscoroutine(rows):
                        rows = await rows

                    for idx, row in enumerate(rows):

                        # --- Use row["name"] if present, otherwise fallback to index ---
                        if isinstance(row, dict) and "name" in row:
                            label = row["name"]
                        else:
                            label = str(idx)

                        case_name = f"{method_name}[{label}]"
                        test_name = f"{cls_name}.{case_name}"
                        mtr = TestResult(case_name, cls_name)

                        async def parameterised_task(method=method, row=row):
                            # dict → kwargs | list/tuple → positional args
                            if isinstance(row, dict):
                                return await self._call(method, **row)
                            return await self._call(method, *row)

                        target = parallel if test_parallel == "methods" else sequential
                        target.append((
                            test_name,
                            parameterised_task,
                            mtr,
                            method_listeners,
                            before_method_methods,
                            after_method_methods
                        ))

                    continue

                # ---------- CASE 2: Normal test (no provider) ----------
                else:
                    case_name = method_name
                    test_name = f"{cls_name}.{case_name}"
                    mtr = TestResult(case_name, cls_name)

                    task = method
                    target = parallel if test_parallel == "methods" else sequential

                    target.append((
                        test_name,
                        task,
                        mtr,
                        method_listeners,
                        before_method_methods,
                        after_method_methods
                    ))

        if test_parallel == "classes":
            # class wrapper: run methods sequentially INSIDE; return dict of per-method results
            async def class_task():
                """
                Class wrapper task:
                  1) run all @before_class hooks
                  2) execute selected test methods sequentially (with
                     before/after_method + listeners)
                  3) always run all @after_class hooks (even on failure)
                  4) if the wrapper bombs, mark any not-yet-run methods as SKIPPED
                """
                results = {}
                ran = set()

                try:
                    # --- 1) Run @before_class hooks first ---
                    for before_class in before_class_methods:
                        try:
                            result = before_class()
                            if inspect.iscoroutine(result):
                                await result

                        except Exception as ex:  # if a before_class fails, skip all methods
                            self._logger.warning(
                                "Exception in before_class '%s' for %s: %s",
                                getattr(before_class, "__name__",
                                        str(before_class)), cls_name, ex)
                            for method_name in selected:
                                tr = TestResult(method_name, cls_name)
                                tr.status = TestStatus.SKIPPED
                                tr.caught_exception = ex
                                results[f"{cls_name}.{method_name}"] = tr
                            # Abort method execution; finally will still run after_class
                            return results

                    # --- 2) Run test methods sequentially ---
                    for method_name in enabled_methods:
                        method = getattr(obj, method_name)
                        provider = getattr(method, "data_provider", None)

                        # ---- Data Provider Case ----
                        if provider:
                            rows = provider()
                            if inspect.iscoroutine(rows):
                                rows = await rows

                            for idx, row in enumerate(rows):

                                # Naming rule
                                if isinstance(row, dict) and "name" in row:
                                    label = row["name"]
                                else:
                                    label = str(idx)

                                case_name = f"{method_name}[{label}]"
                                mtr = TestResult(case_name, cls_name)

                                async def parameterised_task(method=method, row=row):
                                    if isinstance(row, dict):
                                        clean_row = dict(row)
                                        clean_row.pop("name", None)
                                        return await self._call(method, **clean_row)
                                    return await self._call(method, *row)

                                ctx = TaskContext(
                                    listeners=method_listeners,
                                    before_methods=before_method_methods,
                                    after_methods=after_method_methods,
                                    lock=None
                                )

                                res = await self.__run_task(parameterised_task, mtr, ctx)
                                results[f"{cls_name}.{case_name}"] = res
                                ran.add(method_name)

                            continue  # <-- prevents raw run

                        # ---- Normal test (no provider) ----
                        mtr = TestResult(method_name, cls_name)
                        task = method
                        ctx = TaskContext(
                            listeners=method_listeners,
                            before_methods=before_method_methods,
                            after_methods=after_method_methods,
                            lock=None
                        )
                        res = await self.__run_task(task, mtr, ctx)
                        results[f"{cls_name}.{method_name}"] = res
                        ran.add(method_name)

                except Exception as ex:  # pylint: disable=broad-exception-caught
                    # --- 3) Wrapper failure: mark any not-yet-run methods as SKIPPED ---
                    self._logger.warning("Exception in class wrapper for %s: %s", cls_name, ex)
                    for method_name in selected:
                        if method_name in ran:
                            continue
                        tr = TestResult(method_name, cls_name)
                        tr.status = TestStatus.SKIPPED
                        tr.caught_exception = ex
                        results[f"{cls_name}.{method_name}"] = tr

                finally:
                    # --- 4) Always run @after_class hooks ---
                    for after_class in after_class_methods:
                        try:
                            result = after_class()
                            if inspect.iscoroutine(result):
                                await result

                        except Exception as ex2:
                            self._logger.warning("Exception in after_class '%s' for %s: %s",
                                                 getattr(after_class, "__name__", str(after_class)),
                                                 cls_name, ex2)

                return results

            task_name = f"{cls_name}.__class_wrapper__"
            dummy = TestResult("__class_wrapper__", cls_name)
            task = class_task

            if test_parallel == "classes":
                parallel.append((task_name, task, dummy, [], [], []))
            else:
                sequential.append((task_name, task, dummy, [], [], []))

        return sequential, parallel, before_class_methods, after_class_methods

    async def __run_suite_test(self, suite_test: dict, class_fixtures: dict) -> dict:
        """
        Run a single <test> block sequentially, collecting results from its
        classes.

        Returns:
            dict[str, TestResult]: Mapping of "Class.method" to TestResult.
        """
        results = {}
        try:
            for class_conf in suite_test["classes"]:
                seq, _, before_class, after_class = await self._collect_tasks_for_class(
                    class_conf, "none")
                class_name = class_conf["name"]
                class_fixtures[class_name] = {"before": before_class, "after": after_class}

                # seq here are wrapper tasks returning dicts of method results
                for task_info in seq:
                    task = task_info[SequentialTaskIndex.TASK]
                    name = task_info[SequentialTaskIndex.NAME]

                    # If this is the class wrapper, call it DIRECTLY (no lifecycle!)
                    if name.endswith(".__class_wrapper__"):
                        res = await task()
                    else:
                        ctx = TaskContext(
                            listeners=task_info[SequentialTaskIndex.LISTENERS],
                            before_methods=task_info[SequentialTaskIndex.BEFORE_METHODS],
                            after_methods=task_info[SequentialTaskIndex.AFTER_METHODS],
                            lock=None)

                        res = await self.__run_task(
                            task,
                            task_info[SequentialTaskIndex.RESULT],
                            ctx)

                    if isinstance(res, dict):
                        results.update(res)
                    else:
                        results[name] = res

        except Exception as ex:  # pylint: disable=broad-exception-caught
            results.update(self.__handle_test_exception(suite_test, ex))

        return results

    def __handle_test_exception(self, suite_test: dict, ex: Exception) -> dict:
        """
        Handle an exception raised while running a <test> block by marking all its
        methods as SKIPPED.

        Returns:
            dict[str, TestResult]: Mapping of "Class.method" to skipped TestResults.
        """
        results = {}
        for class_conf in suite_test["classes"]:
            cls_name = class_conf["name"]
            cls = self._resolve_class(cls_name)
            obj = cls()
            all_methods = [
                attr for attr in dir(obj)
                if callable(getattr(obj, attr))
                   and getattr(getattr(obj, attr), "is_test", False)
            ]
            selected = self._filter_methods(
                all_methods,
                class_conf.get("methods", {"include": [], "exclude": []}),
            )
            for m in selected:
                tr = TestResult(m, cls_name)
                tr.status = TestStatus.SKIPPED
                tr.caught_exception = ex
                results[f"{cls_name}.{m}"] = tr
        return results

    async def __collect_from_suite(self, suite: dict):
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
            test_parallel = suite_test.get("parallel", suite_conf.get("parallel", "none"))

            if test_parallel == "tests":
                test_name = suite_test.get("name", "UnnamedTest")
                dummy_result = TestResult("__test_wrapper__", test_name)
                parallel_tasks.append((
                    test_name,
                    lambda: self.__run_suite_test(suite_test, class_fixtures),
                    dummy_result,
                    [],
                    [],
                    []
                ))
            else:
                for class_conf in suite_test["classes"]:
                    class_entry = await self._collect_tasks_for_class(class_conf,
                                                                test_parallel)
                    class_name = class_conf["name"]
                    class_fixtures[class_name] = {
                        "before": class_entry[ClassTaskIndex.BEFORE_CLASS],
                        "after": class_entry[ClassTaskIndex.AFTER_CLASS]
                    }
                    sequential_tasks.extend(class_entry[ClassTaskIndex.SEQUENTIAL])
                    parallel_tasks.extend(class_entry[ClassTaskIndex.PARALLEL])

        print(f"sequential_tasks : {sequential_tasks}\n\n")
        print(f"parallel_tasks   : {parallel_tasks}\n\n")
        print(f"class_fixtures   : {class_fixtures}\n\n")

        return sequential_tasks, parallel_tasks, class_fixtures

    async def __run_task(self,
                         task,
                         test_result: TestResult,
                         ctx: TaskContext = None):

        ctx = ctx or TaskContext()

        before_methods = ctx.before_methods or []
        after_methods = ctx.after_methods or []
        listeners = ctx.listeners or []

        lock = ctx.lock or None

        async def _call(func, *args, **kwargs):
            """Call a function whether it's sync or async."""
            result = func(*args, **kwargs)
            if inspect.iscoroutine(result):
                return await result
            return result

        async def _run_task_body():
            try:
                result = task()

                # Await coroutine-based tasks
                if inspect.iscoroutine(result):
                    result = await result

                # If a data-provider wrapped call already returned TestResult or dict, return it
                if isinstance(result, dict):
                    return result

                if isinstance(result, TestResult):
                    return result

                # Old: (status, exception)
                if isinstance(result, tuple) and len(result) == 2:
                    status, ex = result
                    test_result.status = status
                    test_result.caught_exception = ex
                    return test_result

                # Normal success
                test_result.status = TestStatus.SUCCESS
                return test_result

            except AssertionFailure as ex:
                test_result.status = TestStatus.FAILURE
                test_result.caught_exception = ex
                return test_result

            except Exception as ex:
                test_result.status = TestStatus.FAILURE
                test_result.caught_exception = ex
                return test_result

        async def _finalize_task():
            # Run after-method hooks only if not skipped
            if test_result.status != TestStatus.SKIPPED:
                for am in after_methods:
                    await _call(am)

            # Notify listeners
            for listener in listeners:
                if test_result.status is TestStatus.SUCCESS:
                    await _call(listener.on_test_success, test_result)
                elif test_result.status is TestStatus.FAILURE:
                    await _call(listener.on_test_failure, test_result)
                elif test_result.status is TestStatus.SKIPPED:
                    await _call(listener.on_test_skipped, test_result)

            test_result.end_milliseconds = int(time.time() * 1000)

        async def execute():
            test_result.start_milliseconds = int(time.time() * 1000)

            # Run before-method hooks
            for bm in before_methods:
                await _call(bm)

            result = await _run_task_body()
            await _finalize_task()
            return result

        # If task has a lock, wrap execution
        if lock:
            async with lock:
                return await execute()

        return await execute()

    async def _call(self, func, *args, **kwargs):
        result = func(*args, **kwargs)
        if inspect.iscoroutine(result):
            return await result
        return result
