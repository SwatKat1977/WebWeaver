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
from typing import Optional
import wx
import wx.aui
from recording.recording_events import (
    EVT_OPEN_RECORDING,
    EVT_RENAME_RECORDING,
    EVT_DELETE_RECORDING)
from recording_metadata import RecordingMetadata
from studio_solution import StudioSolution
from solution_explorer_node_data import (
    SolutionExplorerNodeData,
    ExplorerNodeType)
from solution_explorer_icons import (load_root_icon,
                                     load_pages_filter_icon,
                                     load_scripts_filter_icon,
                                     load_recordings_filter_icon)

ID_CONTEXT_MENU_REC_OPEN = wx.ID_HIGHEST + 3000
ID_CONTEXT_MENU_REC_RENAME = wx.ID_HIGHEST + 3001
ID_CONTEXT_MENU_REC_DELETE = wx.ID_HIGHEST + 3002


class SolutionExplorerPanel(wx.Panel):

    def __init__(self, parent: wx.Window):
        super().__init__(parent)

        self._tree: Optional[wx.TreeCtrl] = None
        self._placeholder: Optional[wx.StaticText] = None
        self._image_list: Optional[wx.ImageList] = None
        self._context_item = None

        self._icon_solution: int = -1
        self._icon_pages: int = -1
        self._icon_scripts: int = -1
        self._icon_recordings: int = -1

        self._create_controls()
        self.show_no_solution()

    def show_no_solution(self):
        self._tree.DeleteAllItems()
        self._tree.Hide()
        self._placeholder.Show()
        self.Layout()

    def show_solution(self, solution: StudioSolution) -> None:
        self._placeholder.Hide()
        self._tree.Show()

        self.clear()
        self._populate_empty_solution(solution)

        self._tree.ExpandAll()
        self.Layout()

    def clear(self) -> None:
        self._tree.DeleteAllItems()

    def populate_recordings(self,
                            solution: StudioSolution,
                            recordings_node: wx.TreeItemId) -> None:
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
                SolutionExplorerNodeData(ExplorerNodeType.RECORDING_ITEM, rec)
            )

    def  get_selected_recording(self) -> Optional[RecordingMetadata]:
        if not self._context_item or not self._context_item.IsOk():
            return None

        data = self._tree.GetItemData(self._context_item)
        if not data:
            return None

        return data.metadata

    def _create_controls(self):
        sizer = wx.BoxSizer(wx.VERTICAL)

        self._placeholder = wx.StaticText(
            self,
            label="No solution loaded"
        )
        self._placeholder.SetForegroundColour(wx.Colour(120, 120, 120))

        self._tree = wx.TreeCtrl(
            self,
            style=wx.TR_HAS_BUTTONS | wx.TR_LINES_AT_ROOT # | wx.TR_HIDE_ROOT
        )

        self.Bind(wx.EVT_TREE_ITEM_MENU, self._on_item_context_menu)
        self.Bind(wx.EVT_MENU,
                        self._on_open_recording,
                        id=ID_CONTEXT_MENU_REC_OPEN)
        self.Bind(wx.EVT_MENU,
                        self._on_rename_recording,
                        id=ID_CONTEXT_MENU_REC_RENAME)
        '''
        self._tree.Bind(wx.EVT_MENU,
                        self._on_delete_recording,
                        id=ID_CONTEXT_MENU_REC_DELETE)
        '''

        # Image list for solution explorer tree
        self._image_list = wx.ImageList(16, 16, True)

        self._icon_solution = self._image_list.Add(load_root_icon())
        self._icon_pages = self._image_list.Add(load_pages_filter_icon())
        self._icon_scripts = self._image_list.Add(load_scripts_filter_icon())
        self._icon_recordings = self._image_list.Add(load_recordings_filter_icon())

        self._tree.AssignImageList(self._image_list)

        # Layout
        sizer.Add(self._placeholder, 1, wx.ALIGN_CENTER | wx.ALL, 10)
        sizer.Add(self._tree, 1, wx.EXPAND)

        self.SetSizer(sizer)

    def _populate_empty_solution(self, solution: StudioSolution) -> None:
        solution_name: str = f"Solution '{solution.solution_name}'"
        root: wx.TreeItemId = self._tree.AddRoot(
            solution_name,
            self._icon_solution,
            self._icon_solution,
            SolutionExplorerNodeData(ExplorerNodeType.SOLUTION_ROOT,
                                     RecordingMetadata())
        )

        self._append_empty_node(root, "Pages", self._icon_pages)
        self._append_empty_node(root, "Scripts", self._icon_scripts)

        recordings: wx.TreeItemId = self._tree.AppendItem(
            root,
            "Recordings",
            self._icon_recordings,
            self._icon_recordings,
            SolutionExplorerNodeData(ExplorerNodeType.FOLDER_RECORDINGS,
                                     RecordingMetadata()))

        self.populate_recordings(solution, recordings)

    def _append_empty_node(self,
                           parent: wx.TreeItemId,
                           label: str,
                           icon: int) -> wx.TreeItemId:
        node = self._tree.AppendItem(parent, label, icon, icon)
        self._tree.AppendItem(node, "(empty)")
        return node

    def _on_item_context_menu(self, event: wx.TreeEvent) -> None:
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

        else:
            # No menu
            return

        self._context_item = item

        self.PopupMenu(menu)

    def _on_open_recording(self, _event: wx.CommandEvent) -> None:
        recording = self.get_selected_recording()
        if not recording:
            return

        event = wx.CommandEvent(EVT_OPEN_RECORDING)
        event.SetClientData(recording)
        event.SetEventObject(self)

        self.ProcessWindowEvent(event)

    def _on_rename_recording(self, _event: wx.CommandEvent) -> None:

        if not self._context_item.IsOk():
            return

        data = self._tree.GetItemData(self._context_item)

        if  not data or data.node_type != ExplorerNodeType.RECORDING_ITEM:
            return

        evt = wx.CommandEvent(EVT_RENAME_RECORDING)
        evt.SetClientObject(data.metadata.file_path)

        wx.PostEvent(self.GetParent(), evt)

    '''

class SolutionExplorerPanel : public wxPanel {
 public:
    explicit SolutionExplorerPanel(wxWindow* parent);

    void ShowNoSolution();
    void ShowSolution(const StudioSolution& solution);
    void Clear();

    void PopulateRecordings(const StudioSolution& solution,
                            const wxTreeItemId& recordingsNode);

    void RefreshRecordings(const StudioSolution& solution);

    RecordingMetadata* GetSelectedRecording() const;

 private:
    wxTreeCtrl* tree_ = nullptr;
    wxStaticText* placeholder_ = nullptr;
    wxImageList* imageList_ = nullptr;
    wxTreeItemId contextItem_;

    int iconSolution_ = -1;
    int iconPages_ = -1;
    int iconScripts_ = -1;
    int iconRecordings_ = -1;

    void CreateControls();

    void PopulateEmptySolution(const StudioSolution& solution);

    wxTreeItemId AppendEmptyNode(const wxTreeItemId& parent,
                                 const wxString& label,
                                 int icon);

    void OnItemContextMenu(wxTreeEvent& event);  // NOLINT
    void OnOpenRecording(wxCommandEvent&);
    void OnRenameRecording(wxCommandEvent&);
    void OnDeleteRecording(wxCommandEvent&);
};

enum {
    ID_CTXMENU_REC_OPEN = wxID_HIGHEST + 3000,
    ID_CTXMENU_REC_RENAME,
    ID_CTXMENU_REC_DELETE
};

void SolutionExplorerPanel::RefreshRecordings(
    const StudioSolution& solution) {
    if (!tree_)
        return;

    auto root = tree_->GetRootItem();
    if (!root.IsOk())
        return;

    wxTreeItemIdValue cookie;
    auto child = tree_->GetFirstChild(root, cookie);

    while (child.IsOk()) {
        if (tree_->GetItemText(child) == "Recordings") {
            PopulateRecordings(solution, child);
            tree_->Expand(child);
            return;
        }

        child = tree_->GetNextChild(root, cookie);
    }
}







void SolutionExplorerPanel::OnDeleteRecording(wxCommandEvent&) {
    if (!contextItem_.IsOk()) {
        return;
    }

    auto* data = dynamic_cast<ExplorerNodeData*>(
        tree_->GetItemData(contextItem_));

    if (!data || data->GetType() != ExplorerNodeType::RecordingItem) {
        return;
    }

    wxCommandEvent evt(EVT_DELETE_RECORDING);
    evt.SetClientData(new std::filesystem::path(data->GetMetadata().filePath));

    wxPostEvent(GetParent(), evt);
}

    '''
