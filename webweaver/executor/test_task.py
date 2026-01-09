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
from typing import Callable
from test_result import TestResult
from task_context import TaskContext


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
        return await executor._TestExecutor__run_task(self.func,
                                                      self.result,
                                                      ctx)
