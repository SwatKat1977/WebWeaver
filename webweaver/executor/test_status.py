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
import enum


class TestStatus(enum.Enum):
    """
    Enum representing the possible outcomes or states of a test.

    Attributes:
        CREATED (int): Test has been created but not yet executed (-1).
        SUCCESS (int): Test completed successfully (1).
        FAILURE (int): Test execution failed (2).
        SKIPPED (int): Test was skipped and not executed (3).
    """
    CREATED = -1
    SUCCESS = 1
    FAILURE = 2
    SKIPPED = 3
