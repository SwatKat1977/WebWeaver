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
from dataclasses import dataclass
from pathlib import Path

@dataclass
class StudioAppSettings:
    """
    Represents application-wide configuration for WebWeaver Studio.

    This dataclass acts as the in-memory settings model used by the UI
    and persistence layer. It contains strongly-typed configuration
    values that can be:

        - Loaded from persistent storage (via AppSettingsManager)
        - Modified by settings pages
        - Saved back to storage

    The model itself contains no persistence or validation logic —
    it is a pure data container.

    Attributes:
        code_generators_path (Path):
            Filesystem path where plugins are discovered and loaded.

        restore_last_solution (bool):
            Whether the application should automatically reopen the
            last solution on startup.
    """

    code_generators_path: Path

    restore_last_solution: bool = True

    start_maximised: bool = False
