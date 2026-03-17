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
from pathlib import Path
from typing import Optional
import wx
import wx.aui
from webweaver.studio.persistence.test_suite_persistence import TestSuitePersistence
from webweaver.studio.recording.recording_events import (
    EVT_OPEN_RECORDING,
    EVT_RENAME_RECORDING,
    EVT_DELETE_RECORDING,
    EVT_NEW_TEST_SUITE,
    EVT_DELETE_TEST_SUITE,
    EVT_RENAME_TEST_SUITE)
from webweaver.studio.recording_metadata import RecordingMetadata
from webweaver.studio.studio_solution import StudioSolution
from webweaver.studio.solution_explorer_node_data import (
    SolutionExplorerNodeData,
    ExplorerNodeType)
from webweaver.studio.solution_explorer_icons import (
                                       load_root_icon,
                                       load_pages_filter_icon,
                                       load_scripts_filter_icon,
                                       load_recordings_filter_icon,
                                       load_test_suites_filter_icon,
                                       load_test_suite_icon)

# Context menu command IDs for recording items in the solution explorer.s
ID_CONTEXT_MENU_REC_OPEN = wx.ID_HIGHEST + 3000
ID_CONTEXT_MENU_REC_RENAME = wx.ID_HIGHEST + 3001
ID_CONTEXT_MENU_REC_DELETE = wx.ID_HIGHEST + 3002
ID_CONTEXT_MENU_TEST_SUITE_NEW = wx.ID_HIGHEST + 3003
ID_CONTEXT_MENU_TEST_SUITE_DELETE = wx.ID_HIGHEST + 3004
ID_CONTEXT_MENU_TEST_SUITE_RENAME = wx.ID_HIGHEST + 3005

HIDE_DEV_WORK: bool = True


class SolutionExplorerPanel(wx.Panel):
    """
    Tree-based panel displaying the contents of the current solution.

    This panel presents a structured view of the solution, including pages,
    scripts, and recordings. It supports context-sensitive actions on recording
    items such as opening, renaming, and deleting.

    The panel acts as a view/controller layer and communicates user actions to
    the parent window via custom wx events.
    """
    # pylint: disable=too-many-instance-attributes

    def __init__(self, parent: wx.Window):
        """
        Construct a new SolutionExplorerPanel.

        Parameters
        ----------
        parent : wx.Window
            Parent window that owns this panel.
        """
        super().__init__(parent)

        self._tree: Optional[wx.TreeCtrl] = None
        self._placeholder: Optional[wx.StaticText] = None
        self._image_list: Optional[wx.ImageList] = None
        self._context_item = None

        self._icon_solution: int = -1
        self._icon_pages: int = -1
        self._icon_scripts: int = -1
        self._icon_recordings: int = -1
        self._icon_test_suites: int = -1
        self._icon_test_suite: int = -1

        self._create_controls()
        self.show_no_solution()

    def show_no_solution(self):
        """
        Display the panel in the "no solution loaded" state.

        Hides the tree control and shows a placeholder message instead.
        """
        self._tree.DeleteAllItems()
        self._tree.Hide()
        self._placeholder.Show()
        self.Layout()

    def show_solution(self, solution: StudioSolution) -> None:
        """
        Display the contents of the given solution in the explorer tree.

        This clears any existing tree contents and rebuilds the view from
        the provided solution model.

        Parameters
        ----------
        solution : StudioSolution
            The solution whose contents should be displayed.
        """
        self._placeholder.Hide()
        self._tree.Show()

        self.clear()
        self._populate_empty_solution(solution)

        self._tree.ExpandAll()
        self.Layout()

    def clear(self) -> None:
        """
        Clear all items from the solution explorer tree.
        """
        self._tree.DeleteAllItems()

    def _populate_recordings(self,
                             solution: StudioSolution,
                             recordings_node: wx.TreeItemId) -> None:
        """
        Populate the recordings folder node with recording items.

        Any existing children of the recordings node are removed before
        inserting the current set of recordings discovered from the solution.

        Parameters
        ----------
        solution : StudioSolution
            The solution model used to discover recording files.
        recordings_node : wx.TreeItemId
            Tree node representing the "Recordings" folder.
        """
        self._tree.DeleteChildren(recordings_node)

        recordings = solution.discover_recording_files()

        if not recordings:
            self._tree.AppendItem(recordings_node, "(empty)")
            return

        for rec in recordings:
            self._tree.AppendItem(
                recordings_node,
                rec.name,
                self._icon_recordings,
                self._icon_recordings,
                SolutionExplorerNodeData(ExplorerNodeType.RECORDING_ITEM, rec))

    def _populate_test_suites(self,
                              solution: StudioSolution,
                              node: wx.TreeItemId) -> None:
        suite_dir: Path = solution.get_test_suites_directory()
        test_suites = TestSuitePersistence.discover_files(suite_dir)

        if not test_suites:
            self._tree.AppendItem(node, "(empty)")
            return

        for suite in test_suites:
            data = suite.data

            self._tree.AppendItem(
                node,
                data.get("name"),
                self._icon_test_suite,
                self._icon_test_suite,
                SolutionExplorerNodeData(ExplorerNodeType.TEST_SUITES_FILTER,
                                         suite))

    def refresh_recordings(self, solution: StudioSolution):
        """
        Refresh the recordings folder in the tree.

        Locates the "Recordings" node and repopulates it using the provided
        solution model.
        """
        if not self._tree:
            return

        root = self._tree.GetRootItem()
        if not root.IsOk():
            return

        child, cookie = self._tree.GetFirstChild(root)

        while child.IsOk():
            if self._tree.GetItemText(child) == "Recordings":
                self._tree.DeleteChildren(child)
                self._populate_recordings(solution, child)
                self._tree.Expand(child)
                return

            child, cookie = self._tree.GetNextChild(root, cookie)

    def refresh_test_suites(self, solution: StudioSolution):
        """
        Refresh the test suites folder in the tree.

        Locates the "Recordings" node and repopulates it using the provided
        solution model.
        """
        if not self._tree:
            return

        root = self._tree.GetRootItem()
        if not root.IsOk():
            return

        child, cookie = self._tree.GetFirstChild(root)

        while child.IsOk():
            if self._tree.GetItemText(child) == "Test Suites":
                self._tree.DeleteChildren(child)
                self._populate_test_suites(solution, child)
                self._tree.Expand(child)
                return

            child, cookie = self._tree.GetNextChild(root, cookie)

    def  get_selected_metadata(self):
        """
        Get the metadata associated with the current context item.

        Returns
        -------
        Optional[Metadata]
            The selected item's metadata, or ``None`` if no valid
            item is selected.
        """
        if not self._context_item or not self._context_item.IsOk():
            return None

        data = self._tree.GetItemData(self._context_item)
        if not data:
            return None

        return data.metadata

    def _create_controls(self):
        """
        Create and lay out all UI controls for the panel.

        This initializes the tree control, placeholder text, image list,
        event bindings, and layout sizers.
        """
        sizer = wx.BoxSizer(wx.VERTICAL)

        self._placeholder = wx.StaticText(
            self,
            label="No solution loaded")
        self._placeholder.SetForegroundColour(wx.Colour(120, 120, 120))

        self._tree = wx.TreeCtrl(
            self,
            style=wx.TR_HAS_BUTTONS | wx.TR_LINES_AT_ROOT)

        self._tree.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self._on_item_activated)
        self.Bind(wx.EVT_TREE_ITEM_MENU, self._on_item_context_menu)
        self.Bind(wx.EVT_MENU,
                  self._on_open_recording,
                  id=ID_CONTEXT_MENU_REC_OPEN)
        self.Bind(wx.EVT_MENU,
                  self._on_rename_recording,
                  id=ID_CONTEXT_MENU_REC_RENAME)
        self.Bind(wx.EVT_MENU,
                  self._on_delete_recording,
                  id=ID_CONTEXT_MENU_REC_DELETE)

        self.Bind(wx.EVT_MENU,
                  self._on_create_new_test_suite,
                  id=ID_CONTEXT_MENU_TEST_SUITE_NEW)
        self.Bind(wx.EVT_MENU,
                  self._on_delete_test_suite,
                  id=ID_CONTEXT_MENU_TEST_SUITE_DELETE)
        self.Bind(wx.EVT_MENU,
                  self._on_rename_test_suite,
                  id=ID_CONTEXT_MENU_TEST_SUITE_RENAME)

        # Image list for solution explorer tree
        self._image_list = wx.ImageList(16, 16, True)

        self._icon_solution = self._image_list.Add(load_root_icon())
        self._icon_pages = self._image_list.Add(load_pages_filter_icon())
        self._icon_scripts = self._image_list.Add(load_scripts_filter_icon())
        self._icon_recordings = self._image_list.Add(load_recordings_filter_icon())
        self._icon_test_suites = self._image_list.Add(load_test_suites_filter_icon())
        self._icon_test_suite = self._image_list.Add(load_test_suite_icon())
        self._tree.AssignImageList(self._image_list)

        # Layout
        sizer.Add(self._placeholder, 1, wx.ALIGN_CENTER | wx.ALL, 10)
        sizer.Add(self._tree, 1, wx.EXPAND)

        self.SetSizer(sizer)

    def _populate_empty_solution(self, solution: StudioSolution) -> None:
        """
        Populate the tree with the basic folder structure for a solution.

        This creates the root solution node and the Pages, Scripts, and
        Recordings folders, then populates the recordings folder.

        Parameters
        ----------
        solution : StudioSolution
            The solution model used to initialize the tree structure.
        """
        solution_name: str = f"Solution '{solution.solution_name}'"
        root: wx.TreeItemId = self._tree.AddRoot(
            solution_name,
            self._icon_solution,
            self._icon_solution,
            SolutionExplorerNodeData(ExplorerNodeType.SOLUTION_ROOT,
                                     RecordingMetadata()))

        if not HIDE_DEV_WORK:
            self._append_empty_node(root, "Pages", self._icon_pages)
            self._append_empty_node(root, "Scripts", self._icon_scripts)

        recordings: wx.TreeItemId = self._tree.AppendItem(
            root,
            "Recordings",
            self._icon_recordings,
            self._icon_recordings,
            SolutionExplorerNodeData(ExplorerNodeType.FOLDER_RECORDINGS,
                                     RecordingMetadata()))

        self._populate_recordings(solution, recordings)

        test_suites: wx.TreeItemId = self._tree.AppendItem(
            root,
            "Test Suites",
            self._icon_test_suites,
            self._icon_test_suites,
            SolutionExplorerNodeData(ExplorerNodeType.FOLDER_TEST_SUITES,
                                     RecordingMetadata()))

        self._populate_test_suites(solution, test_suites)

    def _append_empty_node(self,
                           parent: wx.TreeItemId,
                           label: str,
                           icon: int) -> wx.TreeItemId:
        """
        Append a folder node containing a single "(empty)" child.

        Parameters
        ----------
        parent : wx.TreeItemId
            Parent tree node.
        label : str
            Display label for the folder.
        icon : int
            Image list index for the folder icon.

        Returns
        -------
        wx.TreeItemId
            The newly created folder node.
        """
        node = self._tree.AppendItem(parent, label, icon, icon)
        self._tree.AppendItem(node, "(empty)")
        return node

    def _on_item_context_menu(self, event: wx.TreeEvent) -> None:
        """
        Handle right-click context menu requests on tree items.

        Displays a context menu when a recording item is right-clicked.
        """
        item: wx.TreeItemId = event.GetItem()
        if not item.IsOk():
            return

        data = self._tree.GetItemData(item)

        if not data:
            return

        menu = wx.Menu()

        if data.node_type == ExplorerNodeType.RECORDING_ITEM:
            menu.Append(ID_CONTEXT_MENU_REC_OPEN, "Open")
            menu.Append(ID_CONTEXT_MENU_REC_RENAME, "Rename")
            menu.AppendSeparator()
            menu.Append(ID_CONTEXT_MENU_REC_DELETE, "Delete")

        elif data.node_type == ExplorerNodeType.FOLDER_TEST_SUITES:
            menu.Append(ID_CONTEXT_MENU_TEST_SUITE_NEW, "Add new test suite")

        elif data.node_type == ExplorerNodeType.TEST_SUITES_FILTER:
            menu.Append(ID_CONTEXT_MENU_TEST_SUITE_DELETE, "Delete suite")
            menu.Append(ID_CONTEXT_MENU_TEST_SUITE_RENAME, "Rename suite")

        else:
            # No menu
            return

        self._context_item = item

        self.PopupMenu(menu)

    def _on_open_recording(self, _event: wx.CommandEvent) -> None:
        """
        Handle the "Open" context menu action for a recording item.

        Posts an EVT_OPEN_RECORDING event to the parent window.
        """
        recording = self.get_selected_metadata()
        if not recording:
            return

        event = wx.CommandEvent(EVT_OPEN_RECORDING)
        event.SetClientData(recording)
        event.SetEventObject(self)

        wx.PostEvent(self.GetParent(), event)

    def _on_rename_recording(self, _event: wx.CommandEvent) -> None:
        """
        Handle the "Rename" context menu action for a recording item.

        Posts an EVT_RENAME_RECORDING event to the parent window.
        """

        if not self._context_item.IsOk():
            return

        data = self._tree.GetItemData(self._context_item)

        if  not data or data.node_type != ExplorerNodeType.RECORDING_ITEM:
            return

        evt = wx.CommandEvent(EVT_RENAME_RECORDING)
        evt.SetClientObject(data.metadata.file_path)

        wx.PostEvent(self.GetParent(), evt)

    def _on_delete_recording(self, _event: wx.CommandEvent) -> None:
        """
        Handle the "Delete" context menu action for a recording item.

        Posts an EVT_DELETE_RECORDING event to the parent window.
        """
        if not self._context_item.IsOk():
            return

        data = self._tree.GetItemData(self._context_item)
        if not data or data.node_type != ExplorerNodeType.RECORDING_ITEM:
            return

        evt: wx.CommandEvent = wx.CommandEvent(EVT_DELETE_RECORDING)
        evt.SetClientData(Path(data.metadata.file_path))

        wx.PostEvent(self.GetParent(), evt)

    def _on_item_activated(self, event: wx.TreeEvent) -> None:
        """
        Handle double-click / Enter on tree items.

        If a recording item is activated, open it.
        """
        item = event.GetItem()
        if not item.IsOk():
            return

        data = self._tree.GetItemData(item)
        if not data:
            return

        if data.node_type != ExplorerNodeType.RECORDING_ITEM:
            return

        # Reuse the same logic path as the context menu
        recording = data.metadata
        if not recording:
            return

        evt = wx.CommandEvent(EVT_OPEN_RECORDING)
        evt.SetClientData(recording)
        evt.SetEventObject(self)

        wx.PostEvent(self.GetParent(), evt)

    def _on_create_new_test_suite(self, _event: wx.CommandEvent) -> None:
        if not self._context_item.IsOk():
            return

        evt: wx.CommandEvent = wx.CommandEvent(EVT_NEW_TEST_SUITE)
        wx.PostEvent(self.GetParent(), evt)

    def _on_delete_test_suite(self, _event: wx.CommandEvent) -> None:
        if not self._context_item.IsOk():
            return

        data = self._tree.GetItemData(self._context_item)
        if not data or data.node_type != ExplorerNodeType.TEST_SUITES_FILTER:
            return

        evt: wx.CommandEvent = wx.CommandEvent(EVT_DELETE_TEST_SUITE)
        evt.SetClientData(Path(data.metadata.path))
        wx.PostEvent(self.GetParent(), evt)

    def _on_rename_test_suite(self, _event: wx.CommandEvent) -> None:
        if not self._context_item.IsOk():
            return

        evt: wx.CommandEvent = wx.CommandEvent(EVT_RENAME_TEST_SUITE)
        wx.PostEvent(self.GetParent(), evt)
