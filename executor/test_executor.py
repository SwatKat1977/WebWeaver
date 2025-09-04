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
import functools
import logging
from concurrent.futures import ThreadPoolExecutor


class TestExecutor:
    def __init__(self, logger: logging.Logger, max_workers: int = 3):
        self._logger = logger.getChild(__name__)
        self._max_workers = max_workers

    def run_tests(self, test_classes):
        sequential_tasks = []
        parallel_tasks = []
        results = {}

        for cls in test_classes:
            obj = cls()

            for attr_name in dir(obj):
                method = getattr(obj, attr_name)

                if callable(method) and getattr(method, "is_test", False):
                    task_name = f"{cls.__name__}.{attr_name}"

                    if method.run_in_parallel:
                        parallel_tasks.append((task_name,
                                               functools.partial(method)))

                    else:
                        sequential_tasks.append((task_name, method))

        self._logger.debug("=== Running Sequential Tests ===")
        for name, task in sequential_tasks:
            results[name] = task()

        self._logger.debug("=== Running Parallel Tests ===")
        with ThreadPoolExecutor(max_workers=self._max_workers) as executor:
            future_map = {executor.submit(task): name for name, task in parallel_tasks}
            for f in future_map:
                results[future_map[f]] = f.result()

        return results
