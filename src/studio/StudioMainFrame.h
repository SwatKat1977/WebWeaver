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

namespace webweaver::studio {

enum class StudioState {
    NoProject,
    ProjectLoaded,
    RecordingRunning,
    RecordingPaused,
    Inspecting
};

struct StudioStateInfo {
    StudioState state = StudioState::NoProject;
};

class StudioMainFrame : public wxFrame {
 public:
    explicit StudioMainFrame(wxWindow* parent = nullptr);

    ~StudioMainFrame();

    void InitAui();

    void SetStudioState(StudioState state);

 private:
    wxAuiManager auiMgr_;
    wxAuiToolBar* toolbar_;

    StudioStateInfo currentStateInfo_;

    // Log area in inspector
    wxTextCtrl* inspectorLog_ = nullptr;

    void CreateMainToolbar();
    void CreateProjectPanel();
    void CreateWorkspacePanel();
    void CreateInspectorPanel();

    void UpdateToolbarState();

    // Inspector event handlers
    void OnInspectorOpenPage(wxCommandEvent &event);
    void OnInspectorStartInspect(wxCommandEvent &event);
    void OnInspectorStopInspect(wxCommandEvent &event);
    void OnInspectorStartRecord(wxCommandEvent &event);
    void OnInspectorStopRecord(wxCommandEvent &event);
    void OnInspectorSaveJson(wxCommandEvent &event);

    void OnNewProjectEvent(wxCommandEvent &event);
    void OnRecordStartStopEvent(wxCommandEvent& event);
    void OnInspectorToggle(wxCommandEvent& event);
};

}   // namespace webweaver::studio

#endif  // STUDIOMAINFRAME_H_
