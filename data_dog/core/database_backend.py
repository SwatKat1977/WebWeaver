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
from abc import ABC, abstractmethod
from typing import Any, Optional


class DatabaseBackend(ABC):

    def connect(self):
        raise NotImplementedError("This backend does not support sync connections.")

    async def connect_async(self):
        raise NotImplementedError("This backend does not support async connections.")

    def execute(self, query, params=None):
        raise NotImplementedError("This backend does not support sync execution.")

    async def execute_async(self, query, params=None):
        raise NotImplementedError("This backend does not support async execution.")

    def insert(self, table, data: dict):
        raise NotImplementedError("This backend does not support sync inserts.")

    async def insert_async(self, table: str, data: dict):
        raise NotImplementedError("This backend does not support async inserts.")

    # ---- Optional capabilities ----
    def get_session(self) -> Optional[Any]:
        """Return a session object if supported; else None."""
        return None

    def supports_sessions(self) -> bool:
        return False

    def supports_async(self) -> bool:
        return False
