"""
This source file is part of Web Weaver
For the latest info, see https://github.com/SwatKat1977/WebWeaver

Copyright 2025-2026 SwatKat1977

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.
"""
import asyncio
import os
from quart import Quart
from webweaver.weavegate.weavegate_service import WeaveGateService

# Quart application instance
app = Quart(__name__)


service = WeaveGateService(app)


async def cancel_background_tasks():
    """
    Cancel and await the application's background task, if it exists.

    This function looks for a task stored on the global ``app`` object
    under the attribute ``background_task``. If found, it cancels the task
    and safely awaits its termination. Any ``asyncio.CancelledError``
    raised during cancellation is suppressed.

    This is typically called during application shutdown to ensure that
    background operations are gracefully stopped.

    Raises:
        asyncio.CancelledError: Only if the cancellation is not suppressed
            (unexpected behavior).
    """
    task = getattr(app, "background_task", None)
    if task:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass


@app.before_serving
async def startup() -> None:
    """
    Code executed before Quart has begun serving http requests.

    returns:
        None
    """
    if not await service.initialise():
        os._exit(1)

    app.background_task = asyncio.create_task(service.run())


@app.after_serving
async def shutdown() -> None:
    """
    Code executed after Quart has stopped serving http requests.

    returns:
        None
    """
    service.shutdown_event.set()

    if app is not None:
        await cancel_background_tasks()
    else:
        print("[WARN] app is not defined at shutdown, skipping cleanup")
