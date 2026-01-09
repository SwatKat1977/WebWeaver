"""
This source file is part of Web Weaver
For the latest info, see https://github.com/SwatKat1977/WebWeaver

Copyright 2025-2026 Webweaver Development Team

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
from dataclasses import dataclass
import inspect
import time
from typing import Callable
from test_result import TestResult
from task_context import TaskContext
from test_status import TestStatus
from assertions import AssertionFailure


@dataclass
class TestTask:
    """
    Represents a single executable test task.

    A Task wraps a callable test function together with its execution result
    and any associated hooks or listeners that should be invoked before and
    after the task runs.
    """

    name: str
    """Human-readable name of the task."""

    func: Callable
    """The callable to execute for this task."""

    result: TestResult
    """Holds the result of the task execution."""

    listeners: list
    """List of listener objects to be notified of task lifecycle events."""

    before_methods: list
    """List of callables to run before executing the task."""

    after_methods: list
    """List of callables to run after executing the task."""

    async def run(self, executor, lock=None):
        ctx = TaskContext(
            listeners=self.listeners,
            before_methods=self.before_methods,
            after_methods=self.after_methods,
            lock=lock
        )

        before_methods = ctx.before_methods or []
        after_methods = ctx.after_methods or []
        listeners = ctx.listeners or []

        async def _call(func, *args, **kwargs):
            result = func(*args, **kwargs)
            if inspect.iscoroutine(result):
                return await result
            return result

        async def _run_task_body():
            try:
                result = self.func()

                if inspect.iscoroutine(result):
                    result = await result

                if isinstance(result, dict):
                    return result

                if isinstance(result, TestResult):
                    return result

                if isinstance(result, tuple) and len(result) == 2:
                    status, ex = result
                    self.result.status = status
                    self.result.caught_exception = ex
                    return self.result

                self.result.status = TestStatus.SUCCESS
                return self.result

            except AssertionFailure as ex:
                self.result.status = TestStatus.FAILURE
                self.result.caught_exception = ex
                return self.result

            except Exception as ex:
                self.result.status = TestStatus.FAILURE
                self.result.caught_exception = ex
                return self.result

        async def _finalize_task():
            if self.result.status != TestStatus.SKIPPED:
                for am in after_methods:
                    await _call(am)

            for listener in listeners:
                if self.result.status is TestStatus.SUCCESS:
                    await _call(listener.on_test_success, self.result)
                elif self.result.status is TestStatus.FAILURE:
                    await _call(listener.on_test_failure, self.result)
                elif self.result.status is TestStatus.SKIPPED:
                    await _call(listener.on_test_skipped, self.result)

            self.result.end_milliseconds = int(time.time() * 1000)

        async def execute():
            self.result.start_milliseconds = int(time.time() * 1000)

            for bm in before_methods:
                await _call(bm)

            result = await _run_task_body()
            await _finalize_task()
            return result

        if lock:
            async with lock:
                return await execute()

        return await execute()
