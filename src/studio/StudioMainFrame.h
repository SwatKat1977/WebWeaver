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
#ifndef MAINWINDOW_H_
#define MAINWINDOW_H_
#include <wx/aui/aui.h>
#include <wx/frame.h>


namespace webweaver::studio {

class StudioMainFrame : public wxFrame {
 public:
    explicit StudioMainFrame(wxWindow* parent = nullptr);

    ~StudioMainFrame();

    void InitAui();

 private:
    wxAuiManager _aui_mgr;

    wxBitmap toolbar_new_project_icon_;
    wxBitmap toolbar_save_project_icon_;
    wxBitmap toolbar_open_icon_;
    wxBitmap toolbar_inspect_icon_;
    wxBitmap toolbar_start_record_icon_;
    wxBitmap toolbar_stop_record_icon_;
    wxBitmap toolbar_pause_icon_;

    void CreateMainToolbar();
};

}

#endif  // MAINWINDOW_H_
