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
#include <wx/artprov.h>
#include "StudioMainFrame.h"
#include "BitmapUtils.h"
#include "ToolbarIcons.h"

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
              wxDEFAULT_FRAME_STYLE)
{
#ifdef __APPLE__
    EnableFullScreenView(false);
#endif

    toolbar_new_project_icon_ = BitmapFromBase64(NEW_PROJECT_BUTTON_ICON.data());
    toolbar_save_project_icon_ = BitmapFromBase64(SAVE_PROJECT_BUTTON_ICON.data());
    toolbar_open_icon_ = BitmapFromBase64(OPEN_BUTTON_ICON.data());
    toolbar_inspect_icon_ = BitmapFromBase64(INSPECT_BUTTON_ICON.data());
    toolbar_start_record_icon_ = BitmapFromBase64(RECORD_BUTTON_ICON.data());
    toolbar_stop_record_icon_ = BitmapFromBase64(STOP_BUTTON_ICON.data());
    toolbar_pause_icon_ = BitmapFromBase64(PAUSE_BUTTON_ICON.data());

    // --------------------------------------------------------------
    // Menu Bar
    // --------------------------------------------------------------
    wxMenuBar *menubar = new wxMenuBar();
    wxMenu *menu = new wxMenu();
    menu->Append(wxID_EXIT, "Quit");
    menubar->Append(menu, "File");
    SetMenuBar(menubar);
}

void StudioMainFrame::InitAui()
{
    _aui_mgr.SetManagedWindow(this);

    // --------------------------------------------------------------
    // TOOLBAR (top, dockable)
    // --------------------------------------------------------------
    CreateMainToolbar();

    _aui_mgr.Update();

    //CentreOnScreen();
}

StudioMainFrame::~StudioMainFrame()
{
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
                    toolbar_new_project_icon_,
                    "New Project");

    toolbar->AddTool(toolbarId_OpenProject,
                    "",
                    toolbar_open_icon_,
                    "Open Project");

    toolbar->AddTool(toolbarId_SaveProject,
                    "",
                    toolbar_save_project_icon_,
                    "Save Project");

    toolbar->AddSeparator();

    toolbar->AddTool(toolbarId_InspectorMode,
                    "",
                    toolbar_inspect_icon_,
                    "Inspector Mode");

    toolbar->AddTool(RECORD_TOOLBAR_ICON_ID,
                     "",
                     toolbar_start_record_icon_,
                     "Record",
                     wxITEM_CHECK);

    toolbar->AddTool(5,
                     "",
                     toolbar_pause_icon_);

    toolbar->Realize();

    /*
    // --- Bind toolbar events ---
    Bind(wxEVT_TOOL,
         on_new_project,
         toolbarId_NewProject);
    Bind(wxEVT_TOOL,
         on_record_toggle,
         START_RECORD_ICON_BMP);
    */

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

}
