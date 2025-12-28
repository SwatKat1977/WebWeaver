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
#include "SolutionExplorerIcons.h"
#include "BitmapUtils.h"
#include "../artworkResources/studio/explorerTreeIcons/recordings_icon.h"
#include "../artworkResources/studio/explorerTreeIcons/root_icon.h"

#include "../artworkResources/studio/explorerTreeIcons/pages_icon.h"
#include "../artworkResources/studio/explorerTreeIcons/scripts_icon.h"

namespace webweaver::studio {

static wxBitmap LoadIcon(const unsigned char* png, const unsigned int size) {
    wxImage img = LoadPngFromMemory(png, size);

    // Force 16 x 16
    img = img.Scale(16, 16, wxIMAGE_QUALITY_HIGH);

    return wxBitmap(img);
}

wxBitmap LoadRootIcon() {
    return LoadIcon(ROOT_ICON,
                    ROOT_ICON_SIZE);
}

wxBitmap LoadRecordingsFilterIcon() {
    return LoadIcon(RECORDINGS_ICON,
                    RECORDINGS_ICON_SIZE);
}

wxBitmap LoadPagesFilterIcon() {
    return LoadIcon(PAGES_ICON,
                    PAGES_ICON_SIZE);
}

wxBitmap LoadScriptsFilterIcon() {
    return LoadIcon(SCRIPTS_ICON,
                    SCRIPTS_ICON_SIZE);
}

}   // namespace webweaver::studio
