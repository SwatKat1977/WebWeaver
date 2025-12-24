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
#include "SolutionExplorerPanel.h"
#include "SolutionExplorerIcons.h"

namespace webweaver::studio {

SolutionExplorerPanel::SolutionExplorerPanel(wxWindow* parent)
    : wxPanel(parent)
{
    CreateControls();
    ShowNoSolution();
}

void SolutionExplorerPanel::CreateControls()
{
    auto* sizer = new wxBoxSizer(wxVERTICAL);

    // Placeholder text
    placeholder_ = new wxStaticText(
        this,
        wxID_ANY,
        "No solution loaded\n\nCreate or open a solution to begin",
        wxDefaultPosition,
        wxDefaultSize,
        wxALIGN_CENTER
    );

    placeholder_->SetForegroundColour(
        wxSystemSettings::GetColour(wxSYS_COLOUR_GRAYTEXT));

    // Tree
    tree_ = new wxTreeCtrl(
        this,
        wxID_ANY,
        wxDefaultPosition,
        wxDefaultSize,
        wxTR_HAS_BUTTONS | wxTR_LINES_AT_ROOT | wxTR_DEFAULT_STYLE
    );

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

void SolutionExplorerPanel::ShowNoSolution()
{
    tree_->DeleteAllItems();
    tree_->Hide();
    placeholder_->Show();

    Layout();
}

void SolutionExplorerPanel::Clear()
{
    tree_->DeleteAllItems();
}

void SolutionExplorerPanel::ShowSolution(const StudioSolution& solution)
{
    placeholder_->Hide();
    tree_->Show();

    Clear();
    PopulateEmptySolution(solution);

    tree_->ExpandAll();
    Layout();
}

void SolutionExplorerPanel::PopulateEmptySolution(
    const StudioSolution& solution)
{
    std::string solutionName = solution.solutionName;
    wxTreeItemId root = tree_->AddRoot(
        "Solution '" + solutionName + "'",
        iconSolution_,
        iconSolution_);

    AppendEmptyNode(root, "Pages", iconPages_);
    AppendEmptyNode(root, "Scripts", iconScripts_);

    wxTreeItemId recordings = tree_->AppendItem(root,
                                                "Recordings",
                                                iconRecordings_,
                                                iconRecordings_);
    PopulateRecordings(solution, recordings);
}

wxTreeItemId SolutionExplorerPanel::AppendEmptyNode(
    const wxTreeItemId& parent,
    const wxString& label,
    int icon)
{
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
            iconRecordings_);
    }
}

}   // namespace webweaver::studio

