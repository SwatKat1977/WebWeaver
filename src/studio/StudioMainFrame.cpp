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
    MERCHimgANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.If not, see < https://www.gnu.org/licenses/>.
*/
#include <wx/artprov.h>
#include <wx/treectrl.h>
#include <filesystem>
#include <fstream>
#include <string>
#include <utility>
#include <vector>
#include "StudioMainFrame.h"
#include "BitmapUtils.h"
#include "ToolbarIcons.h"
#include "SolutionCreateWizard/WizardBasicInfoPage.h"
#include "SolutionCreateWizard/WizardSelectBrowserPage.h"
#include "SolutionCreateWizard/WizardBehaviourPage.h"
#include "SolutionCreateWizard/WizardFinishPage.h"
#include "ProjectWizardControlIDs.h"
#include "SolutionExplorerIcons.h"
#include "StudioSolution.h"

namespace webweaver::studio {


constexpr int TOOLBAR_ID_NEW_SOLUTION = wxID_HIGHEST + 1;
constexpr int TOOLBAR_ID_OPEN_SOLUTION = wxID_HIGHEST + 2;
constexpr int TOOLBAR_ID_SAVE_SOLUTION = wxID_HIGHEST + 3;
constexpr int TOOLBAR_ID_CLOSE_SOLUTION = wxID_HIGHEST + 4;
constexpr int TOOLBAR_ID_INSPECTOR_MODE = wxID_HIGHEST + 5;
constexpr int TOOLBAR_ID_START_STOP_RECORD = wxID_HIGHEST + 6;
constexpr int TOOLBAR_ID_PAUSE_RECORD = wxID_HIGHEST + 7;

constexpr int PAGENO_BASICINFOPAGE = 0;
constexpr int PAGENO_SELECTBROWSERPAGE = 1;
constexpr int PAGENO_BEHAVIOURPAGE = 2;
constexpr int PAGENO_FINISHPAGE = 3;

constexpr int ID_RECENT_SOLUTION_BASE = wxID_HIGHEST + 500;

enum {
    ID_INSPECTOR_OPEN_PAGE = wxID_HIGHEST + 1001,
    ID_INSPECTOR_START_INSPECT,
    ID_INSPECTOR_STOP_INSPECT,
    ID_INSPECTOR_START_RECORD,
    ID_INSPECTOR_STOP_RECORD,
    ID_INSPECTOR_SAVE_JSON
};

// macOS draws menu bar differently and pulls windows upward slightly
#ifdef __APPLE__
wxPoint InitialWindowPosition = wxPoint(0, 30);
#else
wxPoint InitialWindowPosition = wxDefaultPosition;
#endif

StudioMainFrame::StudioMainFrame(wxWindow* parent)
    : wxFrame(nullptr, wxID_ANY,
    "Webweaver Automation Studio",
    InitialWindowPosition,
    wxSize(1024, 768),
    wxDEFAULT_FRAME_STYLE) {
#ifdef __APPLE__
        EnableFullScreenView(false);
#endif

    // --------------------------------------------------------------
    // Menu Bar
    // --------------------------------------------------------------
    wxMenuBar *menubar = new wxMenuBar();

    // -- File Menu --
    wxMenu *fileMenu = new wxMenu();
    fileMenu->Append(wxID_NEW, "New Project\tCtrl+N");
    fileMenu->Append(wxID_OPEN, "Open Project\tCtrl+O");

    recentSolutionsMenu_ = new wxMenu();
    fileMenu->AppendSubMenu(recentSolutionsMenu_, "Recent Solutions");

    fileMenu->Append(wxID_SAVE, "Save Project\tCtrl+S");
    fileMenu->AppendSeparator();
    fileMenu->Append(wxID_EXIT, "Exit\tCtrl-X");
    menubar->Append(fileMenu, "File");
    SetMenuBar(menubar);

    wxMenu* helpMenu = new wxMenu();
    helpMenu->Append(wxID_EXIT, "About");
    menubar->Append(helpMenu, "Help");
    SetMenuBar(menubar);

    recentSolutions_.Load();
    RebuildRecentSolutionsMenu();
}

void StudioMainFrame::InitAui() {
    auiMgr_.SetManagedWindow(this);

    // Reset any previously stored layout
    auiMgr_.LoadPerspective("", true);

    auiMgr_.GetArtProvider()->SetMetric(wxAUI_DOCKART_SASH_SIZE, 2);

    stateController_ = std::make_unique<StudioStateController>(
        [this](StudioState newState) {
            currentState_ = newState;
            UpdateToolbarState();
        });

    // --------------------------------------------------------------
    // TOOLBAR (top, dockable)
    // --------------------------------------------------------------
    CreateMainToolbar();

    stateController_->SetUiReady(true);
    UpdateToolbarState();

    CreateSolutionPanel();

    CreateWorkspacePanel();

    CreateInspectorPanel();

    auiMgr_.Update();
}

StudioMainFrame::~StudioMainFrame() {
    auiMgr_.UnInit();
}

void StudioMainFrame::CreateMainToolbar() {
    toolbar_ = new wxAuiToolBar(
        this,
        -1,
        wxDefaultPosition,
        wxDefaultSize,
        wxNO_BORDER | wxAUI_TB_DEFAULT_STYLE | wxAUI_TB_TEXT |
        wxAUI_TB_HORZ_LAYOUT);
    toolbar_->SetToolBitmapSize(wxSize(32, 32));
    toolbar_->SetToolPacking(5);
    toolbar_->SetToolSeparation(5);

    toolbar_->AddTool(TOOLBAR_ID_NEW_SOLUTION,
        "",
        LoadToolbarNewProjectIcon(),
        "Create New Solution");

    toolbar_->AddTool(TOOLBAR_ID_OPEN_SOLUTION,
        "",
        LoadToolbarOpenProjectIcon(),
        "Open Solution");

    toolbar_->AddTool(TOOLBAR_ID_SAVE_SOLUTION,
        "",
        LoadToolbarSaveProjectIcon(),
        "Save Solution");

    toolbar_->AddTool(TOOLBAR_ID_CLOSE_SOLUTION,
        "",
        LoadToolbarCloseSolutionIcon(),
        "Close Solution");

    toolbar_->AddSeparator();

    toolbar_->AddTool(TOOLBAR_ID_INSPECTOR_MODE,
        "",
        LoadToolbarInspectIcon(),
        "Inspector Mode",
        wxITEM_CHECK);

    toolbar_->AddTool(TOOLBAR_ID_START_STOP_RECORD,
        "",
        LoadToolbarStartRecordIcon(),
        "Record");

    toolbar_->AddTool(TOOLBAR_ID_PAUSE_RECORD,
        "",
        LoadToolbarPauseRecordIcon(),
        "Pause Recording");

    toolbar_->Realize();

    // --- Bind toolbar events ---
    toolbar_->Bind(wxEVT_TOOL,
        &StudioMainFrame::OnNewSolutionEvent,
        this,
        TOOLBAR_ID_NEW_SOLUTION);

    toolbar_->Bind(wxEVT_TOOL,
        &StudioMainFrame::OnCloseSolutionEvent,
        this,
        TOOLBAR_ID_CLOSE_SOLUTION);

    toolbar_->Bind(wxEVT_TOOL,
        &StudioMainFrame::OnOpenSolutionEvent,
        this,
        TOOLBAR_ID_OPEN_SOLUTION);

    toolbar_->Bind(wxEVT_TOOL,
        &StudioMainFrame::OnRecordStartStopEvent,
        this,
        TOOLBAR_ID_START_STOP_RECORD);

    toolbar_->Bind(wxEVT_TOOL,
        &StudioMainFrame::OnRecordPauseEvent,
        this,
        TOOLBAR_ID_PAUSE_RECORD);

    toolbar_->Bind(wxEVT_TOOL,
        &StudioMainFrame::OnInspectorEvent,
        this,
        TOOLBAR_ID_INSPECTOR_MODE);

    auiMgr_.AddPane(
        toolbar_,
        wxAuiPaneInfo()
        .Name("MainToolbar")
        .ToolbarPane()
        .Top()
        .Row(0)
        .Position(0)
        .LeftDockable(false)
        .RightDockable(false)
        .BottomDockable(false)
        .Gripper(false)
        .Floatable(false)
        .Movable(false));

    auiMgr_.Update();
}

void StudioMainFrame::CreateSolutionPanel() {
    // Solution panel (left top)
    solutionExplorerPanel_ = new SolutionExplorerPanel(this);

    auiMgr_.AddPane(solutionExplorerPanel_,
                     wxAuiPaneInfo()
        .Left()
        .Row(1)
        .PaneBorder(false)
        .Caption("Solution Explorer")
        .CloseButton(true)
        .MaximizeButton(true)
        .MinimizeButton(true)
        .BestSize(300, 300));
}

void StudioMainFrame::CreateWorkspacePanel() {
    // -------------------------
    // Workspace
    // -------------------------
    wxPanel *workspacePanel = new wxPanel(this);
    wxBoxSizer *workspaceSizer = new wxBoxSizer(wxVERTICAL);
    workspaceSizer->Add(new wxStaticText(workspacePanel,
                        wxID_ANY,
                        "Workspace"), 0, wxALL, 5);

    workspacePanel->SetSizer(workspaceSizer);

    // Add main central area
    auiMgr_.AddPane(
        workspacePanel,
        wxAuiPaneInfo()
        .CenterPane()
        .Row(1)
        .PaneBorder(false)
        .Caption("Workspace"));
}

void StudioMainFrame::CreateInspectorPanel() {
    // Parent is the main frame (it will be managed as an AUI pane)
    wxPanel* inspectorPanel = new wxPanel(this);

    // Vertical layout: buttons at top, log below
    wxBoxSizer* mainSizer = new wxBoxSizer(wxVERTICAL);

    // --- Button column ---
    wxBoxSizer* buttonSizer = new wxBoxSizer(wxVERTICAL);

    wxButton* btnOpenPage = new wxButton(
        inspectorPanel,
        ID_INSPECTOR_OPEN_PAGE,
        "Open Page");

    wxButton* btnStartInspect = new wxButton(
        inspectorPanel,
        ID_INSPECTOR_START_INSPECT,
        "Start Inspect Mode");

    wxButton* btnStopInspect = new wxButton(
        inspectorPanel,
        ID_INSPECTOR_STOP_INSPECT,
        "Stop Inspect Mode");

    wxButton* btnStartRecord = new wxButton(
        inspectorPanel,
        ID_INSPECTOR_START_RECORD,
        "Start Record Mode");

    wxButton* btnStopRecord = new wxButton(
        inspectorPanel,
        ID_INSPECTOR_STOP_RECORD,
        "Stop Record Mode");

    wxButton* btnSaveJson = new wxButton(
        inspectorPanel,
        ID_INSPECTOR_SAVE_JSON,
        "Save Recording to JSON");

    // Pack buttons with a little spacing
    buttonSizer->Add(btnOpenPage, 0, wxALL | wxEXPAND, 5);
    buttonSizer->Add(btnStartInspect,
                     0,
                     wxLEFT | wxRIGHT | wxBOTTOM | wxEXPAND, 5);
    buttonSizer->Add(btnStopInspect,
                     0,
                     wxLEFT | wxRIGHT | wxBOTTOM | wxEXPAND, 5);
    buttonSizer->Add(btnStartRecord,
                     0,
                     wxLEFT | wxRIGHT | wxBOTTOM | wxEXPAND, 5);
    buttonSizer->Add(btnStopRecord,
                     0,
                     wxLEFT | wxRIGHT | wxBOTTOM | wxEXPAND, 5);
    buttonSizer->Add(btnSaveJson,
                     0,
                     wxLEFT | wxRIGHT | wxBOTTOM | wxEXPAND, 5);

    mainSizer->Add(buttonSizer, 0, wxEXPAND | wxALL, 5);

    // --- Log area (multiline text) ---
    inspectorLog_ = new wxTextCtrl(
        inspectorPanel,
        wxID_ANY,
        "",
        wxDefaultPosition,
        wxDefaultSize,
        wxTE_MULTILINE | wxTE_READONLY);

    mainSizer->Add(inspectorLog_, 1, wxEXPAND | wxLEFT | wxRIGHT | wxBOTTOM, 5);

    inspectorPanel->SetSizer(mainSizer);

    // Register as a dockable pane on the right
    auiMgr_.AddPane(
        inspectorPanel,
        wxAuiPaneInfo()
        .Name("InspectorPanel")
        .Caption("WebWeaver Inspector")
        .Right()
        .Row(1)
        .BestSize(350, 600)
        .CloseButton(true)
        .MaximizeButton(true)
        .MinimizeButton(true)
        .Floatable(true)
        .Movable(true)
        .Dockable(true)
        .Hide());

    // Bind button events
    inspectorPanel->Bind(wxEVT_BUTTON,
        &StudioMainFrame::OnInspectorOpenPage,
        this,
        ID_INSPECTOR_OPEN_PAGE);

    inspectorPanel->Bind(wxEVT_BUTTON,
        &StudioMainFrame::OnInspectorStartInspect,
        this,
        ID_INSPECTOR_START_INSPECT);

    inspectorPanel->Bind(wxEVT_BUTTON,
        &StudioMainFrame::OnInspectorStopInspect,
        this,
        ID_INSPECTOR_STOP_INSPECT);

    inspectorPanel->Bind(wxEVT_BUTTON,
        &StudioMainFrame::OnInspectorStartRecord,
        this,
        ID_INSPECTOR_START_RECORD);

    inspectorPanel->Bind(wxEVT_BUTTON,
        &StudioMainFrame::OnInspectorStopRecord,
        this,
        ID_INSPECTOR_STOP_RECORD);

    inspectorPanel->Bind(wxEVT_BUTTON,
        &StudioMainFrame::OnInspectorSaveJson,
        this,
        ID_INSPECTOR_SAVE_JSON);
}

void StudioMainFrame::OnInspectorOpenPage(wxCommandEvent& event) {
    if (inspectorLog_) {
        inspectorLog_->AppendText("Open Page clicked\n");
    }
}

void StudioMainFrame::OnInspectorStartInspect(wxCommandEvent& event) {
    if (inspectorLog_) {
        inspectorLog_->AppendText("Start Inspect Mode\n");
    }
}

void StudioMainFrame::OnInspectorStopInspect(wxCommandEvent& event) {
    if (inspectorLog_) {
        inspectorLog_->AppendText("Stop Inspect Mode\n");
    }
}

void StudioMainFrame::OnInspectorStartRecord(wxCommandEvent& event) {
    if (inspectorLog_) {
        inspectorLog_->AppendText("Start Record Mode\n");
    }
}

void StudioMainFrame::OnInspectorStopRecord(wxCommandEvent& event) {
    if (inspectorLog_) {
        inspectorLog_->AppendText("Stop Record Mode\n");
    }
}

void StudioMainFrame::OnInspectorSaveJson(wxCommandEvent& event) {
    if (inspectorLog_) {
        inspectorLog_->AppendText("Save Recording to JSON\n");
    }
}

void StudioMainFrame::OnNewSolutionEvent(wxCommandEvent& event) {
    ProjectCreateWizardData data;
    std::vector<std::string> steps = {
    "Basic solution info",
    "Browser selection",
    "Configure behaviour",
    "Finish"
    };

    int pageNumber = PAGENO_BASICINFOPAGE;

    while (true) {
        wxDialog* wizardDialog = nullptr;

        switch (pageNumber) {
        case PAGENO_BASICINFOPAGE:
            wizardDialog = new WizardBasicInfoPage(this, &data, steps);
            break;

        case PAGENO_SELECTBROWSERPAGE:
            wizardDialog = new WizardSelectBrowserPage(this, &data, steps);
            break;

        case PAGENO_BEHAVIOURPAGE:
            wizardDialog = new WizardBehaviourPage(this, &data, steps);
            break;

        case PAGENO_FINISHPAGE:
            wizardDialog = new WizardFinishPage(this, &data, steps);
            break;

        default:
            // No more pages .. end wizard and create solution

            currentSolution_.emplace(
                data.solutionName,
                data.solutionDirectory,
                data.createSolutionDir,
                data.baseUrl,
                data.browser);

            if (!SaveSolutionToDisk(currentSolution_.value())) {
                return;
            }

            stateController_->OnSolutionLoaded();

            solutionExplorerPanel_->ShowSolution(currentSolution_.value());

            recentSolutions_.AddSolution(
                currentSolution_->GetSolutionFilePath());
            recentSolutions_.Save();
            RebuildRecentSolutionsMenu();

            recordingSession_ = std::make_unique<RecordingSession>(
                currentSolution_.value());

            return;
        }

        int rc = wizardDialog->ShowModal();
        wizardDialog->Destroy();

        if (rc == wxID_CANCEL) {
            // Wizard cancelled, abort
            return;
        }

        if (rc == PROJECT_WIZARD_BACK_BUTTON_ID) {
            pageNumber -= 1;
            continue;

        } else if (rc == wxID_OK) {
            pageNumber += 1;
            continue;
        }

        // Unknown return code, exit cleanly.
        return;
    }
}

void StudioMainFrame::OnCloseSolutionEvent(wxCommandEvent& event) {
    currentSolution_.reset();
    stateController_->OnSolutionClosed();

    solutionExplorerPanel_->ShowNoSolution();
}

void StudioMainFrame::OnOpenSolutionEvent(wxCommandEvent& event) {
    wxFileDialog dlg(
        this,
        "Open Webweaver Studio solution",
        wxEmptyString,
        wxEmptyString,
        "Webweaver Solution (*.wws)|*.wws",
        wxFD_OPEN | wxFD_FILE_MUST_EXIST);

    if (dlg.ShowModal() == wxID_OK) {
        wxString path = dlg.GetPath();

        if (OpenSolution(path.ToStdString())) {
            stateController_->OnSolutionLoaded();
            solutionExplorerPanel_->ShowSolution(currentSolution_.value());

            recordingSession_ = std::make_unique<RecordingSession>(currentSolution_.value());
        }
    }
}

void StudioMainFrame::OnRecordStartStopEvent(wxCommandEvent& event) {
    stateController_->OnRecordStartStop();
}

void StudioMainFrame::OnRecordPauseEvent(wxCommandEvent& event) {
    stateController_->OnRecordPause();

    switch (stateController_->GetState()) {
    case StudioState::RecordingRunning:
        recordingSession_->Start("Untitled Recording");
        break;
     
    case StudioState::SolutionLoaded:
        recordingSession_->Stop();
        solutionExplorerPanel_->RefreshRecordings(currentSolution_.value());
        break;

    default:
        break;
    }
}

void StudioMainFrame::OnInspectorEvent(wxCommandEvent& event) {
    wxAuiPaneInfo& pane = auiMgr_.GetPane("InspectorPanel");
    if (!pane.IsOk()) {
        return;
    }

    bool show = !pane.IsShown();
    pane.Show(show);
    auiMgr_.Update();

    stateController_->OnInspectorToggle(show);
}

void StudioMainFrame::UpdateToolbarState() {
    // First: disable everything that is state-dependent
    toolbar_->EnableTool(TOOLBAR_ID_SAVE_SOLUTION, false);
    toolbar_->EnableTool(TOOLBAR_ID_CLOSE_SOLUTION, false);
    toolbar_->EnableTool(TOOLBAR_ID_INSPECTOR_MODE, false);
    toolbar_->EnableTool(TOOLBAR_ID_START_STOP_RECORD, false);
    toolbar_->EnableTool(TOOLBAR_ID_PAUSE_RECORD, false);

    bool hasActiveRecording = false;
    bool isInspecting = false;
    bool isPaused = false;

    switch (currentState_) {
    case StudioState::NoSolution:
        // Only New/Open make sense
        break;

    case StudioState::SolutionLoaded:
        toolbar_->EnableTool(TOOLBAR_ID_SAVE_SOLUTION, true);
        toolbar_->EnableTool(TOOLBAR_ID_CLOSE_SOLUTION, true);
        toolbar_->EnableTool(TOOLBAR_ID_INSPECTOR_MODE, true);
        toolbar_->EnableTool(TOOLBAR_ID_START_STOP_RECORD, true);

        break;

    case StudioState::RecordingRunning:
        toolbar_->EnableTool(TOOLBAR_ID_START_STOP_RECORD, true);
        toolbar_->EnableTool(TOOLBAR_ID_PAUSE_RECORD, true);
        hasActiveRecording = true;
        break;

    case StudioState::RecordingPaused:
        toolbar_->EnableTool(TOOLBAR_ID_START_STOP_RECORD, true);
        toolbar_->EnableTool(TOOLBAR_ID_PAUSE_RECORD, true);
        hasActiveRecording = true;
        isPaused = true;
        break;

    case StudioState::Inspecting:
        toolbar_->EnableTool(TOOLBAR_ID_SAVE_SOLUTION, true);
        toolbar_->EnableTool(TOOLBAR_ID_CLOSE_SOLUTION, true);
        toolbar_->EnableTool(TOOLBAR_ID_START_STOP_RECORD, false);
        toolbar_->EnableTool(TOOLBAR_ID_INSPECTOR_MODE, true);
        isInspecting = true;
        break;
    }

    // Handle active recording states
    if (hasActiveRecording) {
        toolbar_->SetToolBitmap(TOOLBAR_ID_START_STOP_RECORD,
            LoadToolbarStopRecordIcon());
        toolbar_->SetToolShortHelp(TOOLBAR_ID_START_STOP_RECORD,
            "Stop Recording");
    } else {
        toolbar_->SetToolBitmap(TOOLBAR_ID_START_STOP_RECORD,
            LoadToolbarStartRecordIcon());
        toolbar_->SetToolShortHelp(TOOLBAR_ID_START_STOP_RECORD,
            "Start Recording");
    }

    // Handle active recording paused states
    if (isPaused) {
        toolbar_->SetToolBitmap(TOOLBAR_ID_PAUSE_RECORD,
            LoadToolbarResumeRecordIcon());
        toolbar_->SetToolShortHelp(TOOLBAR_ID_PAUSE_RECORD,
            "Resume Recording");
    } else {
        toolbar_->SetToolBitmap(TOOLBAR_ID_PAUSE_RECORD,
            LoadToolbarPauseRecordIcon());
        toolbar_->SetToolShortHelp(TOOLBAR_ID_PAUSE_RECORD,
            "Pause Recording");
    }

    // Handle Inspector Mode toggle button
    toolbar_->ToggleTool(TOOLBAR_ID_INSPECTOR_MODE, isInspecting);

    toolbar_->Realize();
    toolbar_->Refresh();
}

bool StudioMainFrame::SaveSolutionToDisk(const StudioSolution& solution) {
    // Ensure solution + subdirectories exist
    if (solution.EnsureDirectoryStructure() !=
        SolutionDirectoryCreateStatus::None) {
        return false;
    }

    const std::filesystem::path solutionFile =
        solution.GetSolutionFilePath();

    // Serialize to JSON
    const nlohmann::json j = solution.ToJson();

    std::ofstream out(solutionFile, std::ios::trunc);
    if (!out.is_open()) {
        return false;
    }

    out << j.dump(4);
    return true;
}


void StudioMainFrame::RebuildRecentSolutionsMenu() {
    // Remove all existing items
    while (recentSolutionsMenu_->GetMenuItemCount() > 0) {
        recentSolutionsMenu_->Destroy(
            recentSolutionsMenu_->FindItemByPosition(0));
    }

    int id = ID_RECENT_SOLUTION_BASE;

    for (const auto& path : recentSolutions_.GetSolutions()) {
        recentSolutionsMenu_->Append(id, path.string());
        Bind(wxEVT_MENU,
            &StudioMainFrame::OnOpenRecentSolutionEvent,
            this,
            id);
        ++id;
    }
}

void StudioMainFrame::OnOpenRecentSolutionEvent(wxCommandEvent& evt) {
    int index = evt.GetId() - ID_RECENT_SOLUTION_BASE;
    OpenSolution(recentSolutions_.GetSolutions()[index]);
}

bool StudioMainFrame::OpenSolution(const std::filesystem::path& solutionFile) {
    if (!std::filesystem::exists(solutionFile)) {
        wxMessageBox("Solution file does not exist.",
            "Open Solution",
            wxICON_ERROR);
        return false;
    }

    nlohmann::json json;

    try {
        std::ifstream in(solutionFile);
        in >> json;
    }
    catch (const std::exception& e) {
        wxMessageBox(
            wxString::Format("Failed to read solution file:\n%s", e.what()),
            "Open Solution",
            wxICON_ERROR);
        return false;
    }

    // Move into current solution
    SolutionLoadResult result = StudioSolution::FromJson(json);

    if (!result.solution.has_value()) {
        wxMessageBox(
            SolutionLoadErrorToStr(result.error),
            "Open Solution",
            wxICON_ERROR);
        return false;
    }

    currentSolution_ = std::move(result.solution.value());

    // Ensure directory structure (safe, idempotent)
    if (currentSolution_->EnsureDirectoryStructure() !=
        SolutionDirectoryCreateStatus::None) {
        wxMessageBox("Failed to prepare solution folders.",
                     "Open Solution", wxICON_ERROR);
        currentSolution_.reset();
        return false;
    }

    // Update state + UI
    stateController_->OnSolutionLoaded();
    solutionExplorerPanel_->ShowSolution(currentSolution_.value());

    // Recent solutions
    recentSolutions_.AddSolution(solutionFile);
    recentSolutions_.Save();
    RebuildRecentSolutionsMenu();

    return true;
}

}   // namespace webweaver::studio
