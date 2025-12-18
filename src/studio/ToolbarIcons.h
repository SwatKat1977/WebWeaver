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
#ifndef TOOLBARICONS_H_
#define TOOLBARICONS_H_

#include <wx/wx.h>

namespace webweaver::studio {

wxBitmap LoadToolbarInspectIcon();

wxBitmap LoadToolbarNewProjectIcon();

wxBitmap LoadToolbarOpenProjectIcon();

wxBitmap LoadToolbarSaveProjectIcon();

wxBitmap LoadToolbarCloseSolutionIcon();

wxBitmap LoadToolbarPauseRecordIcon();

wxBitmap LoadToolbarStartRecordIcon();

wxBitmap LoadToolbarStopRecordIcon();

wxBitmap LoadToolbarResumeRecordIcon();

}   // namespace webweaver::studio

#endif  // TOOLBARICONS_H_
