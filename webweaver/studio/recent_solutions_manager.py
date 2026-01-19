"""
This source file is part of Web Weaver
For the latest info, see https://github.com/SwatKat1977/WebWeaver

Copyright 2025 SwatKat1977

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
import json
from pathlib import Path
import wx

class RecentSolutionsManager:
    """
    Manages the list of recently opened solutions.

    This class is responsible for loading, saving, and maintaining a bounded
    list of recently opened solution files. The list is persisted to disk in
    JSON format under the user's configuration directory.

    The most recently added solution is always stored at the front of the list.
    Duplicate entries are automatically de-duplicated, and the list is capped
    to a fixed maximum size.

    Storage format (JSON):
        {
            "version": 1,
            "recentSolutions": [
                "path/to/solution1.wws",
                "path/to/solution2.wws"
            ]
        }
    """

    MAX_RECENT: int = 10

    def __init__(self):
        """
        Construct a new RecentSolutionsManager with an empty recent list.

        Call :meth:`load` to populate the list from persistent storage.
        """
        self._recent: list[Path] = []

    def load(self) -> None:
        """
        Load the recent solutions list from disk.

        If the storage file does not exist or cannot be read, the internal
        recent list is left empty.

        Any existing in-memory entries are discarded before loading.
        """
        self._recent.clear()

        path = self._get_storage_path()
        if not path.exists():
            return

        try:
            with path.open("r", encoding="utf-8") as f:
                j = json.load(f)
        except (OSError, json.JSONDecodeError):
            return

        entries = j.get("recentSolutions", [])
        for entry in entries:
            self._recent.append(Path(entry))

    def save(self) -> None:
        """
        Save the current recent solutions list to disk.

        The storage directory is created if it does not already exist.
        The file is written in JSON format with human-readable indentation.
        """
        j = {
            "version": 1,
            "recentSolutions": [str(p) for p in self._recent],
        }

        path = self._get_storage_path()
        path.parent.mkdir(parents=True, exist_ok=True)

        with path.open("w", encoding="utf-8") as f:
            json.dump(j, f, indent=2)

    def add_solution(self, solution_path: Path | str) -> None:
        """
        Add a solution to the recent list.

        If the solution already exists in the list, it is moved to the front.
        The list is truncated to :data:`MAX_RECENT` entries if necessary.

        This method automatically saves the updated list to disk.

        Parameters
        ----------
        solution_path : Path or str
            Path to the solution file to add.
        """
        path = Path(solution_path)

        # Remove if already present
        self._recent = [p for p in self._recent if p != path]

        # Insert at front
        self._recent.insert(0, path)

        # Truncate if larger then max size
        if len(self._recent) > self.MAX_RECENT:
            self._recent = self._recent[: self.MAX_RECENT]

        self.save()

    def _get_storage_path(self) -> Path:
        """
        Get the path to the recent solutions storage file.

        Returns
        -------
        Path
            Path to the JSON file used to store the recent solutions list.
        """
        base_dir = Path(wx.StandardPaths.Get().GetUserConfigDir())
        return base_dir / "webweaver" / "recent_solutions.json"

    def get_solutions(self) -> list[Path]:
        """
        Get the current list of recent solutions.

        Returns
        -------
        list[Path]
            A copy of the list of recent solution paths, ordered from most
            recent to least recent.
        """
        return list(self._recent)
