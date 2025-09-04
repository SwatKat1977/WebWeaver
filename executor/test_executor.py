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
from concurrent.futures import ThreadPoolExecutor
import functools
import logging
import time
from test_result import TestResult


class TestExecutor:
    def __init__(self, logger: logging.Logger, max_workers: int = 3):
        self._logger = logger.getChild(__name__)
        self._max_workers = max_workers

    def run_tests(self, test_classes):
        sequential_tasks = []
        parallel_tasks = []

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
                                                 method,
                                                 results_obj))

        sequential_results: dict = self.__run_sequential_tests(sequential_tasks)
        parallel_results: dict = self.__run_parallel_tests(parallel_tasks)
        return sequential_results | parallel_results

    def __run_sequential_tests(self, sequential_tasks: list) -> dict:
        results: dict = {}

        self._logger.debug("================================")
        self._logger.debug("=== Running Sequential Tests ===")
        self._logger.debug("================================")

        for name, task, test_result in sequential_tasks:
            current_time_ms: int = int(time.time() * 1000)
            test_result.start_milliseconds = current_time_ms
            print((f"[DEBUG] sequential results info: {test_result.method_name}::"
                   f"{test_result.test_class} "
                   f"started {test_result.start_milliseconds}"))

            task_result = task()
            print(f"TAsk result: {task_result}")
            results[name] = task_result

        return results

    def __run_parallel_tests(self, parallel_tasks: list) -> dict:
        results: dict = {}

        self._logger.debug("=== Running Parallel Tests ===")
        with ThreadPoolExecutor(max_workers=self._max_workers) as executor:
            future_map = {executor.submit(task):
                              name for name, task,
                              test_result in parallel_tasks}
            for f in future_map:
                results[future_map[f]] = f.result()

        return results
