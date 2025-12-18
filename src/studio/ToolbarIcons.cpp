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
#include "ToolbarIcons.h"
#include "BitmapUtils.h"
#include "../artworkResources/studio/toolbar/toolbar_inspect.h"
#include "../artworkResources/studio/toolbar/toolbar_new_project.h"
#include "../artworkResources/studio/toolbar/toolbar_open_project.h"
#include "../artworkResources/studio/toolbar/toolbar_pause_record.h"
#include "../artworkResources/studio/toolbar/toolbar_save_project.h"
#include "../artworkResources/studio/toolbar/toolbar_start_record.h"
#include "../artworkResources/studio/toolbar/toolbar_stop_record.h"
#include "../artworkResources/studio/toolbar/toolbar_resume_record.h"

namespace webweaver::studio {

static wxBitmap LoadToolbarIcon(const unsigned char *png,
                                const unsigned int size) {
    wxImage img = LoadPngFromMemory(png, size);

    // Force 32 x 32
    img = img.Scale(32, 32, wxIMAGE_QUALITY_HIGH);

    return wxBitmap(img);
}

wxBitmap LoadToolbarInspectIcon() {
    return LoadToolbarIcon(INSPECT_ICON,
                           INSPECT_ICON_SIZE);
}

wxBitmap LoadToolbarNewProjectIcon() {
    return LoadToolbarIcon(NEW_PROJECT_ICON,
                           NEW_PROJECT_ICON_SIZE);
}

wxBitmap LoadToolbarOpenProjectIcon() {
    return LoadToolbarIcon(OPEN_PROJECT_ICON,
                           OPEN_PROJECT_ICON_SIZE);
}

wxBitmap LoadToolbarPauseRecordIcon() {
    return LoadToolbarIcon(PAUSE_RECORD_ICON,
                           PAUSE_RECORD_ICON_SIZE);
}

wxBitmap LoadToolbarSaveProjectIcon() {
    return LoadToolbarIcon(SAVE_PROJECT_ICON,
                           SAVE_PROJECT_ICON_SIZE);
}

wxBitmap LoadToolbarStartRecordIcon() {
    return LoadToolbarIcon(START_RECORD_ICON,
                           START_RECORD_ICON_SIZE);
}

wxBitmap LoadToolbarStopRecordIcon() {
    return LoadToolbarIcon(STOP_RECORD_ICON,
                           STOP_RECORD_ICON_SIZE);
}

wxBitmap LoadToolbarResumeRecordIcon() {
    return LoadToolbarIcon(RESUME_RECORD_ICON,
                           RESUME_RECORD_ICON_SIZE);
}

}   // namespace webweaver::studio
