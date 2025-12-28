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
#include <wx/aui/auibook.h>
#include "WorkspacePanel.h"
#include "RecordingViewerPanel.h"

namespace webweaver::studio {

WorkspacePanel::WorkspacePanel(wxWindow* parent)
    : wxPanel(parent) {
    CreateUI();
}

void WorkspacePanel::CreateUI() {
    auto* sizer = new wxBoxSizer(wxVERTICAL);

    notebook_ = new wxAuiNotebook(
        this,
        wxID_ANY,
        wxDefaultPosition,
        wxDefaultSize,
        wxAUI_NB_TOP | wxAUI_NB_TAB_MOVE);

    sizer->Add(notebook_, 1, wxEXPAND);
    SetSizer(sizer);
}

void WorkspacePanel::OpenRecording(const RecordingViewContext& ctx) {
    if (IsRecordingOpen(ctx.recordingFile)) {
        // focus existing tab
        return;
    }

    auto* viewer = new RecordingViewerPanel(notebook_, ctx);
    notebook_->AddPage(viewer, ctx.metadata.name, true);
}

bool WorkspacePanel::IsRecordingOpen(const wxFileName& file) const {
    if (!notebook_)
        return false;

    wxFileName target(file);
    target.Normalize(wxPATH_NORM_ABSOLUTE |
                     wxPATH_NORM_DOTS |
                     wxPATH_NORM_TILDE);

    for (size_t i = 0; i < notebook_->GetPageCount(); ++i)
    {
        auto* page = notebook_->GetPage(i);

        auto* viewer =
            dynamic_cast<RecordingViewerPanel*>(page);

        if (!viewer)
            continue;

        wxFileName openFile = viewer->GetRecordingFile();
        openFile.Normalize(wxPATH_NORM_ABSOLUTE |
                           wxPATH_NORM_DOTS |
                           wxPATH_NORM_TILDE);

        if (openFile == target)
            return true;
    }

    return false;
}

}   // namespace webweaver::studio
