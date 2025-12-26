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
#ifndef SOLUTIONEXPLORERPANEL_H_
#define SOLUTIONEXPLORERPANEL_H_
#include <wx/panel.h>
#include <wx/treectrl.h>
#include <wx/stattext.h>
#include "StudioSolution.h"
#include "RecordingMetadata.h"

namespace webweaver::studio {

class SolutionExplorerPanel : public wxPanel {
 public:
    explicit SolutionExplorerPanel(wxWindow* parent);

    void ShowNoSolution();
    void ShowSolution(const StudioSolution& solution);
    void Clear();

    void PopulateRecordings(const StudioSolution& solution,
                            const wxTreeItemId& recordingsNode);

    void RefreshRecordings(const StudioSolution& solution);

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

}   // namespace webweaver::studio

#endif  // SOLUTIONEXPLORERPANEL_H_
