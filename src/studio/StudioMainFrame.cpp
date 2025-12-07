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
#include "StudioMainFrame.h"

namespace webweaver::studio {

StudioMainFrame::StudioMainFrame(wxWindow* parent)
    : wxFrame(nullptr, wxID_ANY,
              "Webweaver Automation Studio",
              wxDefaultPosition,
              wxSize(1400, 900),
              wxDEFAULT_FRAME_STYLE)
{
#ifdef __APPLE__
    EnableFullScreenView(false);
#endif
}

void StudioMainFrame::InitAui()
{
    m_mgr.SetManagedWindow(this);

    // Add panes here later...
    // m_mgr.AddPane(...);

    m_mgr.Update();
}

StudioMainFrame::~StudioMainFrame()
{
    m_mgr.UnInit();
}

}
