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
    """
    Enumeration of node types used in the Solution Explorer tree.

    This enum identifies the semantic role of each tree node, allowing
    the UI and event handlers to distinguish between solution roots,
    logical folders, and individual recording items.
    """

    SOLUTION_ROOT = enum.auto()
    FOLDER_PAGES = enum.auto()
    FOLDER_SCRIPTS = enum.auto()
    FOLDER_RECORDINGS = enum.auto()
    RECORDING_ITEM = enum.auto()


class SolutionExplorerNodeData:
    """
    Data container attached to nodes in the Solution Explorer tree.

    Instances of this class are stored as item data on tree nodes and
    provide structured access to the node's type and associated model
    object (such as recording metadata).

    This allows the tree UI to remain lightweight while still supporting
    context-sensitive actions like opening, renaming, or deleting items.
    """

    def __init__(self,
                 node_type: ExplorerNodeType,
                 metadata: RecordingMetadata):
        """
        Create a new SolutionExplorerNodeData instance.

        Parameters
        ----------
        node_type : ExplorerNodeType
            The type of the tree node.
        metadata : RecordingMetadata
            Metadata associated with the node, typically representing a
            recording item. May be ``None`` for non-recording nodes.
        """
        super().__init__()
        self._node_type = node_type
        self._recording = metadata

    @property
    def node_type(self) -> ExplorerNodeType:
        """
        Get the type of this explorer node.

        Returns
        -------
        ExplorerNodeType
            The node type associated with this tree item.
        """
        return self._node_type

    @property
    def metadata(self) -> RecordingMetadata:
        """
        Get the metadata associated with this explorer node.

        Returns
        -------
        RecordingMetadata
            The metadata object attached to this node. For recording nodes,
            this contains information such as name, file path, and timestamps.
        """
        return self._recording
