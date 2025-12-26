/*
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
*/
#include <string>
#include "SolutionExplorerPanel.h"
#include "SolutionExplorerIcons.h"
#include "SolutionExplorerNodeData.h"

namespace webweaver::studio {

enum {
    ID_CTXMENU_REC_OPEN = wxID_HIGHEST + 3000,
    ID_CTXMENU_REC_RENAME,
    ID_CTXMENU_REC_DELETE
};

SolutionExplorerPanel::SolutionExplorerPanel(wxWindow* parent)
    : wxPanel(parent) {
    CreateControls();
    ShowNoSolution();
}

void SolutionExplorerPanel::CreateControls() {
    auto* sizer = new wxBoxSizer(wxVERTICAL);

    // Placeholder text
    placeholder_ = new wxStaticText(
        this,
        wxID_ANY,
        "No solution loaded\n\nCreate or open a solution to begin",
        wxDefaultPosition,
        wxDefaultSize,
        wxALIGN_CENTER);

    placeholder_->SetForegroundColour(
        wxSystemSettings::GetColour(wxSYS_COLOUR_GRAYTEXT));

    // Tree
    tree_ = new wxTreeCtrl(
        this,
        wxID_ANY,
        wxDefaultPosition,
        wxDefaultSize,
        wxTR_HAS_BUTTONS | wxTR_LINES_AT_ROOT | wxTR_DEFAULT_STYLE);

    tree_->Bind(wxEVT_TREE_ITEM_MENU,
                &SolutionExplorerPanel::OnItemContextMenu,
                this);

    Bind(wxEVT_MENU,
         &SolutionExplorerPanel::OnOpenRecording,
         this,
         ID_CTXMENU_REC_OPEN);
    Bind(wxEVT_MENU,
         &SolutionExplorerPanel::OnRenameRecording,
         this,
         ID_CTXMENU_REC_RENAME);
    Bind(wxEVT_MENU,
         &SolutionExplorerPanel::OnDeleteRecording,
         this,
         ID_CTXMENU_REC_DELETE);

    // Image list
    imageList_ = new wxImageList(16, 16, true);

    iconSolution_ = imageList_->Add(LoadRootIcon());
    iconPages_ = imageList_->Add(LoadPagesFilterIcon());
    iconScripts_ = imageList_->Add(LoadScriptsFilterIcon());
    iconRecordings_ = imageList_->Add(LoadRecordingsFilterIcon());

    tree_->AssignImageList(imageList_);

    // Layout
    sizer->Add(placeholder_, 1, wxEXPAND | wxALL, 10);
    sizer->Add(tree_, 1, wxEXPAND | wxALL, 5);

    SetSizer(sizer);
}

void SolutionExplorerPanel::ShowNoSolution() {
    tree_->DeleteAllItems();
    tree_->Hide();
    placeholder_->Show();

    Layout();
}

void SolutionExplorerPanel::Clear() {
    tree_->DeleteAllItems();
}

void SolutionExplorerPanel::ShowSolution(const StudioSolution& solution) {
    placeholder_->Hide();
    tree_->Show();

    Clear();
    PopulateEmptySolution(solution);

    tree_->ExpandAll();
    Layout();
}

void SolutionExplorerPanel::PopulateEmptySolution(
    const StudioSolution& solution) {
    std::string solutionName = solution.solutionName;
    wxTreeItemId root = tree_->AddRoot(
        "Solution '" + solutionName + "'",
        iconSolution_,
        iconSolution_,
        new ExplorerNodeData(ExplorerNodeType::SolutionRoot));

    AppendEmptyNode(root, "Pages", iconPages_);
    AppendEmptyNode(root, "Scripts", iconScripts_);

    wxTreeItemId recordings = tree_->AppendItem(
        root,
        "Recordings",
        iconRecordings_,
        iconRecordings_,
        new ExplorerNodeData(ExplorerNodeType::FolderRecordings));
    PopulateRecordings(solution, recordings);
}

wxTreeItemId SolutionExplorerPanel::AppendEmptyNode(
    const wxTreeItemId& parent,
    const wxString& label,
    int icon) {
    auto node = tree_->AppendItem(parent, label, icon, icon);
    tree_->AppendItem(node, "(empty)");
    return node;
}

void SolutionExplorerPanel::PopulateRecordings(
    const StudioSolution& solution,
    const wxTreeItemId& recordingsNode) {
    tree_->DeleteChildren(recordingsNode);

    auto recordings = solution.DiscoverRecordingFiles();

    if (recordings.empty()) {
        tree_->AppendItem(recordingsNode, "(empty)");
        return;
    }

    for (const auto& rec : recordings) {
        tree_->AppendItem(
            recordingsNode,
            rec.name,
            iconRecordings_,
            iconRecordings_,
            new ExplorerNodeData(ExplorerNodeType::RecordingItem));
    }
}

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

void SolutionExplorerPanel::OnItemContextMenu(wxTreeEvent& event) {
    wxTreeItemId item = event.GetItem();
    if (!item.IsOk()) {
        return;
    }

    auto* data = dynamic_cast<ExplorerNodeData*>(
    tree_->GetItemData(item));

    if (!data) {
        return;
    }

    wxMenu menu;

    switch (data->GetType()) {
    case ExplorerNodeType::RecordingItem:
        menu.Append(ID_CTXMENU_REC_OPEN, "Open");
        menu.Append(ID_CTXMENU_REC_RENAME, "Rename");
        menu.AppendSeparator();
        menu.Append(ID_CTXMENU_REC_DELETE, "Delete");
        break;

    default:
        return; // no menu
    }

    contextItem_ = item;

    PopupMenu(&menu);
}

void SolutionExplorerPanel::OnOpenRecording(wxCommandEvent&) {
    wxLogMessage("Open recording");
}

void SolutionExplorerPanel::OnRenameRecording(wxCommandEvent&) {
    wxString oldName = tree_->GetItemText(contextItem_);

    wxTextEntryDialog dlg(
        this,
        "Rename recording",
        "Rename",
        oldName);

    if (dlg.ShowModal() != wxID_OK) {
        return;
    }

    tree_->SetItemText(contextItem_, dlg.GetValue());
}

void SolutionExplorerPanel::OnDeleteRecording(wxCommandEvent&) {
    if (wxMessageBox(
        "Delete this recording?",
        "Confirm",
        wxYES_NO | wxICON_WARNING) != wxYES) {
        return;
    }

    tree_->Delete(contextItem_);
}

}   // namespace webweaver::studio

