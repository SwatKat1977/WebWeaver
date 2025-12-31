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
#include <chrono>   // NOLINT
#include <fstream>
#include <sstream>
#include "RecordingEvent.h"
#include "RecordingSession.h"
#include "UUID.h"

namespace webweaver::studio {


static std::string NowUtcIso() {
    auto now = std::chrono::system_clock::now();
    std::time_t t = std::chrono::system_clock::to_time_t(now);

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

    const std::string id = GenerateUuidV4();

    recordingJson_ = {
        { "version", 1 },
        { "recording", {
            { "id", id },
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

    nextIndex_ = 0;
    startTime_ = std::chrono::steady_clock::now();

    return true;
}

void RecordingSession::Stop() {
    if (!active_) {
        return;
    }

    std::ofstream out(filePath_, std::ios::trunc);
    if (out.is_open()) {
        out << recordingJson_.dump(4);
    }

    active_ = false;
}

void RecordingSession::AppendEvent(RecordingEventType type,
                                   nlohmann::json payload) {
    if (!active_) {
        return;
    }

    const auto now = std::chrono::steady_clock::now();
    const auto elapsed =
        std::chrono::duration_cast<std::chrono::milliseconds>(
            now - startTime_).count();

    RecordingEvent event;
    event.index = nextIndex_++;
    event.timestampMs = static_cast<uint64_t>(elapsed);
    event.type = type;
    event.payload = std::move(payload);

    // Append to in-memory JSON
    recordingJson_["recording"]["events"].push_back({
        { "index", event.index },
        { "timestamp", event.timestampMs },
        { "type", EventTypeToString(event.type) },
        { "payload", event.payload }
    });

    FlushToDisk();
}

void RecordingSession::FlushToDisk()
{
    std::ofstream out(filePath_, std::ios::trunc);
    if (!out.is_open())
        return;

    out << recordingJson_.dump(4);
}

}   // namespace webweaver::studio
