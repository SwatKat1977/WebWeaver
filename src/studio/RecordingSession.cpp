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
#include <chrono>
#include <fstream>
#include <sstream>
#include "RecordingSession.h"

namespace webweaver::studio {


static std::string NowUtcIso()
{
    using namespace std::chrono;
    auto now = system_clock::now();
    std::time_t t = system_clock::to_time_t(now);

    std::tm tm{};
#ifdef _WIN32
    gmtime_s(&tm, &t);
#else
    gmtime_r(&t, &tm);
#endif

    std::ostringstream oss;
    oss << std::put_time(&tm, "%Y-%m-%dT%H:%M:%SZ");
    return oss.str();
}

RecordingSession::RecordingSession(const StudioSolution& solution)
    : solution_(solution) {
}

bool RecordingSession::Start(const std::string& name) {
    if (active_) {
        return false;
    }

    const auto recordingsDir = solution_.GetRecordingsDirectory();
    std::filesystem::create_directories(recordingsDir);

    const auto filename =
        name + "_" + NowUtcIso() + ".wwrec";

    filePath_ = recordingsDir / filename;

    recordingJson_ = {
        { "version", 1 },
        { "recording", {
            { "id", "PLACEHOLDER" },
            { "name", name },
            { "createdAt", NowUtcIso() },
            { "browser", solution_.selectedBrowser },
            { "baseUrl", solution_.baseUrl },
            { "steps", nlohmann::json::array() }
        }}
    };

    std::ofstream out(filePath_, std::ios::trunc);
    if (!out.is_open())
        return false;

    out << recordingJson_.dump(4);
    active_ = true;
    return true;
}

void RecordingSession::Stop()
{
    if (!active_) {
        return;
    }

    std::ofstream out(filePath_, std::ios::trunc);
    if (out.is_open()) {
        out << recordingJson_.dump(4);
    }

    active_ = false;
}

}   // namespace webweaver::studio
