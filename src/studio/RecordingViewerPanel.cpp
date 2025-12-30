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
#include "RecordingViewerPanel.h"

namespace webweaver::studio {

wxString FormatTimePoint(
    const std::chrono::system_clock::time_point& tp) {
    std::time_t tt =
        std::chrono::system_clock::to_time_t(tp);

    std::tm tm{};
#if defined(_WIN32)
    localtime_s(&tm, &tt);
#else
    localtime_r(&tt, &tm);
#endif

    char buffer[64];
    std::strftime(buffer, sizeof(buffer),
                  "%Y-%m-%d %H:%M:%S", &tm);

    return wxString::FromUTF8(buffer);
}

RecordingViewerPanel::RecordingViewerPanel(wxWindow* parent,
                                           const RecordingViewContext& ctx)
    : wxPanel(parent),
      context_(ctx) {
    CreateUI();
}

void RecordingViewerPanel::CreateUI() {
    auto* mainSizer = new wxBoxSizer(wxVERTICAL);

    auto* title = new wxStaticText(
        this,
        wxID_ANY,
        context_.metadata.name);

    title->SetFont(
        title->GetFont().Bold().Larger());

    mainSizer->Add(title, 0, wxALL, 10);

    auto addField = [&](const wxString& label,
                        const wxString& value) {
        auto* row = new wxBoxSizer(wxHORIZONTAL);

        row->Add(
            new wxStaticText(this, wxID_ANY, label),
            0, wxRIGHT, 5);

        row->Add(
            new wxStaticText(this, wxID_ANY, value),
            1);

        mainSizer->Add(row, 0, wxLEFT | wxRIGHT | wxBOTTOM, 10);
    };

    addField("File:", context_.recordingFile.GetFullName());
    addField("Path:", context_.recordingFile.GetPath());
    addField("Recorded:", FormatTimePoint(context_.metadata.createdAt));

    SetSizerAndFit(mainSizer);
}

const std::string& RecordingViewerPanel::GetRecordingId() const {
    return context_.metadata.id;
}

const wxFileName& RecordingViewerPanel::GetRecordingFile() const {
    return context_.recordingFile;
}

}   // namespace webweaver::studio
