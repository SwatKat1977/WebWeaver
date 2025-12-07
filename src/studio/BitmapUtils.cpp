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
#include "wx/mstream.h"
#include "wx/base64.h"
#include "BitmapUtils.h"

namespace webweaver::studio {

std::string CleanBase64(const char* data) {
    std::string out;
    out.reserve(strlen(data));

    for (const char* p = data; *p; ++p) {
        unsigned char c = static_cast<unsigned char>(*p);

        // Keep only valid base64 characters: A-Z a-z 0-9 + / =
        if ((c >= 'A' && c <= 'Z') ||
            (c >= 'a' && c <= 'z') ||
            (c >= '0' && c <= '9') ||
            c == '+' || c == '/' || c == '=')
        {
            out.push_back(c);
        }
    }

    return out;
}

wxBitmap BitmapFromBase64(const char *base64Data,
                          const wxSize& size) {
    // ---- Clean the base64 (removes newlines, spaces, tabs) ----
    std::string clean = CleanBase64(base64Data);

    // ---- Decode ----
    wxMemoryBuffer buffer = wxBase64Decode(clean.c_str());
    if (buffer.IsEmpty()) {
        wxLogError("Failed to decode base64 image data.");
        return wxBitmap();
    }

    // Create input stream from buffer
    wxMemoryInputStream stream(buffer.GetData(), buffer.GetDataLen());

    // Load image from stream
    wxImage image(stream, wxBITMAP_TYPE_ANY);
    if (!image.IsOk()) {
        wxLogError("Failed to load wxImage from decoded data.");
        return wxBitmap();
    }

    // Resize if needed
    if (size != wxDefaultSize) {
        image = image.Scale(size.x, size.y, wxIMAGE_QUALITY_HIGH);
    }

    return wxBitmap(image);
}

}
