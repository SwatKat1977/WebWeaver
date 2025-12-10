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
#include "StudioMainFrame.h"
#include "BitmapUtils.h"
#include "ToolbarIcons.h"
#include "ProjectCreateWizard/WizardBasicInfoPage.h"
#include "ProjectWizardControlIDs.h"

namespace webweaver::studio {

constexpr int RECORD_TOOLBAR_ICON_ID = 100;

#ifdef __APPLE__
    // macOS draws menu bar differently and pulls windows upward slightly
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
    wxMenu *menu = new wxMenu();
    menu->Append(wxID_EXIT, "Quit");
    menubar->Append(menu, "File");
    SetMenuBar(menubar);
}

void StudioMainFrame::InitAui() {
    _aui_mgr.SetManagedWindow(this);

    // Reset any previously stored layout
    _aui_mgr.LoadPerspective("", true);

    // --------------------------------------------------------------
    // TOOLBAR (top, dockable)
    // --------------------------------------------------------------
    CreateMainToolbar();

    CreateProjectPanel();

    CreateWorkspacePanel();

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
        "Inspector Mode");

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
        .Caption("Project Explorer")
        .CloseButton(true)
        .MaximizeButton(true)
        .MinimizeButton(true)
        .BestSize(300, 300));
}

void StudioMainFrame::CreateWorkspacePanel() {
}

void StudioMainFrame::OnNewProjectEvent(wxCommandEvent& event) {
    ProjectCreateWizardData data;
    std::vector<std::string> steps = {
    "Basic solution info",
    "Browser selection",
    "Configure behaviour",
    "Finish"
    };

    int pageNumber = 1;

    while (true) {
        wxDialog* wizardDialog = nullptr;

        switch (pageNumber) {
        case 1:
            wizardDialog = new WizardBasicInfoPage(this, &data, steps);
            break;

        case 2:
            return;
            // wizardDialog = WizardWebSelectBrowserPage(self, data);
            break;

        case 3:
            // wizardDialog = WizardWebBehaviourPage(self, data)
            break;

        case 4:
            // wizardDialog = WizardFinishPage(self, data)

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
        }
        else if (rc == wxID_OK) {
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

}   // namespace webweaver::studio
