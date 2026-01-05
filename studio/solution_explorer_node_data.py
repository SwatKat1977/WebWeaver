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
import enum
from recording_metadata import RecordingMetadata


class ExplorerNodeType(enum.Enum):
    SOLUTION_ROOT = enum.auto()
    FOLDER_PAGES = enum.auto()
    FOLDER_SCRIPTS = enum.auto()
    FOLDER_RECORDINGS = enum.auto()
    RECORDING_ITEM = enum.auto()


class SolutionExplorerNodeData:
    def __init__(self,
                 node_type: ExplorerNodeType,
                 metadata: RecordingMetadata):
        super().__init__()
        self._node_type = node_type
        self._recording = metadata

    @property
    def node_type(self) -> ExplorerNodeType:
        return self._node_type

    @property
    def metadata(self) -> RecordingMetadata:
        return self._recording
