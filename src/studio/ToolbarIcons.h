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

wxBitmap LoadToolbarStartRecordIcon();

// -----------------------
// Record Button Icon (Base64)
// -----------------------
extern const char RECORD_BUTTON_ICON[];

// -----------------------
// Pause Button Icon (Base64)
// -----------------------
extern const char PAUSE_BUTTON_ICON[];

// -----------------------
// Inspect Button Icon (Base64)
// -----------------------
extern const char INSPECT_BUTTON_ICON[];

// -----------------------
// Open Button Icon (Base64)
// -----------------------
extern const char OPEN_BUTTON_ICON[];

// -----------------------
// New Project Button Icon (Base64)
// -----------------------
extern const char NEW_PROJECT_BUTTON_ICON[];

// -----------------------
// Stop Button Icon (Base64)
// -----------------------
extern const char STOP_BUTTON_ICON[];

// -----------------------
// Save Project Button Icon (Base64)
// -----------------------
extern const char SAVE_PROJECT_BUTTON_ICON[];

}

#endif
