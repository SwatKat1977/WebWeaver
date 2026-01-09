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
import threading
import typing


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
