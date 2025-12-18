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
#ifndef STUDIOMAINFRAME_H_
#define STUDIOMAINFRAME_H_
#include <wx/aui/aui.h>
#include <wx/frame.h>
#include <memory>
#include <optional>
#include "StudioStateController.h"
#include "StudioSolution.h"

namespace webweaver::studio {

class StudioMainFrame : public wxFrame {
 public:
    explicit StudioMainFrame(wxWindow* parent = nullptr);

    ~StudioMainFrame();

    void InitAui();

 private:
    wxAuiManager auiMgr_;
    wxAuiToolBar* toolbar_;

    std::unique_ptr<StudioStateController> stateController_;
    StudioState currentState_ = StudioState::NoProject;
    std::optional<StudioSolution> currentSolution_;

    // Log area in inspector
    wxTextCtrl* inspectorLog_ = nullptr;

    void CreateMainToolbar();
    void CreateSolutionPanel();
    void CreateWorkspacePanel();
    void CreateInspectorPanel();

    void UpdateToolbarState();

    // Inspector event handlers
    // wxWidgets event handlers require non-const wxCommandEvent&

    // ---- Inspector Events ----

    // NOLINTNEXTLINE(runtime/references)
    void OnInspectorOpenPage(wxCommandEvent &event);

    // NOLINTNEXTLINE(runtime/references)
    void OnInspectorStartInspect(wxCommandEvent &event);

    // NOLINTNEXTLINE(runtime/references)
    void OnInspectorStopInspect(wxCommandEvent &event);

    // NOLINTNEXTLINE(runtime/references)
    void OnInspectorStartRecord(wxCommandEvent &event);

    // NOLINTNEXTLINE(runtime/references)
    void OnInspectorStopRecord(wxCommandEvent &event);

    // NOLINTNEXTLINE(runtime/references)
    void OnInspectorSaveJson(wxCommandEvent &event);


    // ---- Main Frame Events ----

    // NOLINTNEXTLINE(runtime/references)
    void OnNewSolutionEvent(wxCommandEvent &event);

    // NOLINTNEXTLINE(runtime/references)
    void OnCloseSolutionEvent(wxCommandEvent& event);

    // NOLINTNEXTLINE(runtime/references)
    void OnRecordStartStopEvent(wxCommandEvent& event);

    // NOLINTNEXTLINE(runtime/references)
    void OnRecordPauseEvent(wxCommandEvent& event);

    // NOLINTNEXTLINE(runtime/references)
    void OnInspectorEvent(wxCommandEvent& event);
};

}   // namespace webweaver::studio

#endif  // STUDIOMAINFRAME_H_
