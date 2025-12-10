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

#include "BrowserIcons.h"
#include "BitmapUtils.h"
#include "imgResources/BrowserLogos/browser_chromium_icon.h"
#include "imgResources/BrowserLogos/browser_firefox_icon.h"
#include "imgResources/BrowserLogos/browser_google_chrome_icon.h"
#include "imgResources/BrowserLogos/browser_microsoft_edge_icon.h"

namespace webweaver::studio {

static wxBitmap LoadIcon(const unsigned char* png, const unsigned int size) {
    wxImage img = LoadPngFromMemory(png, size);

    // Force 32 x 32
    img = img.Scale(32, 32, wxIMAGE_QUALITY_HIGH);

    return wxBitmap(img);
}

wxBitmap LoadBrowserIconChromium() {
    return LoadIcon(BROWSER_CHROMIUM_ICON,
                    BROWSER_CHROMIUM_ICON_SIZE);
}

wxBitmap LoadBrowserIconFirefox() {
    return LoadIcon(BROWSER_FIREFOX_ICON,
                    BROWSER_FIREFOX_ICON_SIZE);
}

wxBitmap LoadBrowserIconGoogleChromium() {
    return LoadIcon(BROWSER_GOOGLE_CHROME_ICON,
                    BROWSER_GOOGLE_CHROME_ICON_SIZE);
}

wxBitmap LoadBrowserIconMicrosoftEdge() {
    return LoadIcon(BROWSER_MICROSOFT_EDGE_ICON,
                    BROWSER_MICROSOFT_EDGE_ICON_SIZE);
}

}   // namespace webweaver::studio
