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
#include <string>
#include <vector>
#include "StudioMainFrame.h"
#include "BitmapUtils.h"
#include "ToolbarIcons.h"
#include "ProjectCreateWizard/WizardBasicInfoPage.h"
#include "ProjectCreateWizard/WizardSelectBrowserPage.h"
#include "ProjectCreateWizard/WizardBehaviourPage.h"
#include "ProjectCreateWizard/WizardFinishPage.h"
#include "ProjectWizardControlIDs.h"

namespace webweaver::studio {

constexpr int RECORD_TOOLBAR_ICON_ID = 100;

constexpr int PAGENO_BASICINFOPAGE = 0;
constexpr int PAGENO_SELECTBROWSERPAGE = 1;
constexpr int PAGENO_BEHAVIOURPAGE = 2;
constexpr int PAGENO_FINISHPAGE = 3;

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
    fileMenu->Append(wxID_EXIT, "New Project");
    fileMenu->Append(wxID_EXIT, "Open Project");
    fileMenu->Append(wxID_EXIT, "Save Project");
    fileMenu->Append(wxID_EXIT, "Exit");
    menubar->Append(fileMenu, "File");
    SetMenuBar(menubar);

    wxMenu* helpMenu = new wxMenu();
    helpMenu->Append(wxID_EXIT, "About");
    menubar->Append(helpMenu, "Help");
    SetMenuBar(menubar);
}

void StudioMainFrame::InitAui() {
    _aui_mgr.SetManagedWindow(this);

    // Reset any previously stored layout
    _aui_mgr.LoadPerspective("", true);

    _aui_mgr.GetArtProvider()->SetMetric(wxAUI_DOCKART_SASH_SIZE, 2);

    // --------------------------------------------------------------
    // TOOLBAR (top, dockable)
    // --------------------------------------------------------------
    CreateMainToolbar();

    CreateProjectPanel();

    CreateWorkspacePanel();

    CreateInspectorPanel();

    _aui_mgr.Update();
}

StudioMainFrame::~StudioMainFrame() {
    _aui_mgr.UnInit();
}

void StudioMainFrame::CreateMainToolbar() {
    const int toolbarId_NewProject = 1;
    const int toolbarId_OpenProject = 2;
    const int toolbarId_SaveProject = 3;
    const int toolbarId_InspectorMode = 4;

    wxAuiToolBar *toolbar = new wxAuiToolBar(
        this,
        -1,
        wxDefaultPosition,
        wxDefaultSize,
        wxNO_BORDER | wxAUI_TB_DEFAULT_STYLE | wxAUI_TB_TEXT |
        wxAUI_TB_HORZ_LAYOUT);
    toolbar->SetToolBitmapSize(wxSize(32, 32));
    toolbar->SetToolPacking(5);
    toolbar->SetToolSeparation(5);

    toolbar->AddTool(toolbarId_NewProject,
        "",
        LoadToolbarNewProjectIcon(),
        "New Project");

    toolbar->AddTool(toolbarId_OpenProject,
        "",
        LoadToolbarOpenProjectIcon(),
        "Open Project");

    toolbar->AddTool(toolbarId_SaveProject,
        "",
        LoadToolbarSaveProjectIcon(),
        "Save Project");

    toolbar->AddSeparator();

    toolbar->AddTool(toolbarId_InspectorMode,
        "",
        LoadToolbarInspectIcon(),
        "Inspector Mode",
        wxITEM_CHECK);

    toolbar->AddTool(RECORD_TOOLBAR_ICON_ID,
        "",
        LoadToolbarStartRecordIcon(),
        "Record",
        wxITEM_CHECK);

    toolbar->AddTool(5,
        "",
        LoadToolbarPauseRecordIcon(),
        "Pause Recording");

    toolbar->Realize();

    // --- Bind toolbar events ---
    Bind(wxEVT_TOOL,
        &StudioMainFrame::OnNewProjectEvent,
        this,
        toolbarId_NewProject);
    Bind(wxEVT_TOOL,
        &StudioMainFrame::OnRecordToggleEvent,
        this,
        RECORD_TOOLBAR_ICON_ID);

    Bind(wxEVT_TOOL,
        &StudioMainFrame::OnInspectorToggle,
        this,
        toolbarId_InspectorMode);

    _aui_mgr.AddPane(
        toolbar,
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

    _aui_mgr.Update();
}

void StudioMainFrame::CreateProjectPanel() {
    // Projects panel (left top)
    wxPanel* projectPanel = new wxPanel(this);
    wxBoxSizer* projectSizer = new wxBoxSizer(wxVERTICAL);

    wxTreeCtrl* projectTree = new wxTreeCtrl(
        projectPanel,
        wxID_ANY,
        wxDefaultPosition,
        wxDefaultSize,
        wxTR_HAS_BUTTONS | wxTR_DEFAULT_STYLE);
    projectSizer->Add(projectTree, 1, wxEXPAND | wxALL, 5);

    projectTree->ExpandAll();

    projectPanel->SetSizer(projectSizer);

    _aui_mgr.AddPane(projectPanel,
                     wxAuiPaneInfo()
        .Left()
        .Row(1)
        .PaneBorder(false)
        .Caption("Project Explorer")
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
    _aui_mgr.AddPane(
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
    _inspectorLog = new wxTextCtrl(
        inspectorPanel,
        wxID_ANY,
        "",
        wxDefaultPosition,
        wxDefaultSize,
        wxTE_MULTILINE | wxTE_READONLY);

    mainSizer->Add(_inspectorLog, 1, wxEXPAND | wxLEFT | wxRIGHT | wxBOTTOM, 5);

    inspectorPanel->SetSizer(mainSizer);

    // Register as a dockable pane on the right
    _aui_mgr.AddPane(
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
    if (_inspectorLog)
        _inspectorLog->AppendText("Open Page clicked\n");
}

void StudioMainFrame::OnInspectorStartInspect(wxCommandEvent& event) {
    if (_inspectorLog)
        _inspectorLog->AppendText("Start Inspect Mode\n");
}

void StudioMainFrame::OnInspectorStopInspect(wxCommandEvent& event) {
    if (_inspectorLog)
        _inspectorLog->AppendText("Stop Inspect Mode\n");
}

void StudioMainFrame::OnInspectorStartRecord(wxCommandEvent& event) {
    if (_inspectorLog)
        _inspectorLog->AppendText("Start Record Mode\n");
}

void StudioMainFrame::OnInspectorStopRecord(wxCommandEvent& event) {
    if (_inspectorLog)
        _inspectorLog->AppendText("Stop Record Mode\n");
}

void StudioMainFrame::OnInspectorSaveJson(wxCommandEvent& event) {
    if (_inspectorLog)
        _inspectorLog->AppendText("Save Recording to JSON\n");
}

void StudioMainFrame::OnNewProjectEvent(wxCommandEvent& event) {
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

            /*
            // Wizard has finished normally:
            for (auto& [key, val] : data) {
                std::cout << key << ": " << val << std::endl;
            }
            */
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

void StudioMainFrame::OnRecordToggleEvent(wxCommandEvent& event) {
    // Retrieve the toolbar from the AUI manager
    wxAuiPaneInfo& pane = _aui_mgr.GetPane("MainToolbar");
    if (!pane.IsOk()) {
        return;
    }

    wxAuiToolBar* toolbar = wxDynamicCast(pane.window, wxAuiToolBar);

    wxWindow* win = pane.window;
    if (!toolbar) {
        return;
    }

    bool isRecording = toolbar->GetToolToggled(RECORD_TOOLBAR_ICON_ID);
    if (isRecording) {
        toolbar->SetToolBitmap(RECORD_TOOLBAR_ICON_ID,
                               LoadToolbarStopRecordIcon());
        toolbar->SetToolShortHelp(RECORD_TOOLBAR_ICON_ID, "Stop Recording");
    } else {
        toolbar->SetToolBitmap(RECORD_TOOLBAR_ICON_ID,
                               LoadToolbarStartRecordIcon());
        toolbar->SetToolShortHelp(RECORD_TOOLBAR_ICON_ID, "Start Recording");
    }

    toolbar->Realize();
}

void StudioMainFrame::OnInspectorToggle(wxCommandEvent& event) {
    wxAuiPaneInfo& pane = _aui_mgr.GetPane("InspectorPanel");
    if (!pane.IsOk())
        return;

    bool show = !pane.IsShown();
    pane.Show(show);

    // keep toolbar button state in sync
    wxAuiPaneInfo& tbPane = _aui_mgr.GetPane("MainToolbar");
    if (tbPane.IsOk()) {
        wxAuiToolBar* toolbar = wxDynamicCast(tbPane.window, wxAuiToolBar);
        if (toolbar) {
            toolbar->ToggleTool(event.GetId(), show);
            toolbar->Refresh();
        }
    }

    _aui_mgr.Update();
}

}   // namespace webweaver::studio
