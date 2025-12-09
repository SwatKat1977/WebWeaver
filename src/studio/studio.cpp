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
#include <wx/wx.h>
#include "StudioMainFrame.h"

class WebweaverStudioApp : public wxApp {
 public:
    bool OnInit() override;
};

wxIMPLEMENT_APP(WebweaverStudioApp);

bool WebweaverStudioApp::OnInit() {
    // Required for PNG/JPEG/etc.
    wxInitAllImageHandlers();

    auto* frame = new webweaver::studio::StudioMainFrame(nullptr);
    frame->Show(true);
    SetTopWindow(frame);

    // IMPORTANT: delay AUI initialisation until AFTER the window is shown
    frame->CallAfter([frame]{
        frame->InitAui();
    });

    return true;
}
