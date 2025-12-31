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
#ifndef RECORDING_RECORDINGSESSION_H_
#define RECORDING_RECORDINGSESSION_H_
#include <filesystem>
#include <string>
#include <nlohmann/json.hpp>
#include "StudioSolution.h"
#include "RecordingEventType.h"

namespace webweaver::studio {

class RecordingSession {
 public:
    explicit RecordingSession(const StudioSolution& solution);

    bool Start(const std::string& name);
    void Stop();

    bool IsRecording() const { return active_; }

    // Appends a single immutable event to the recording.
    // - Index and timestamp are assigned internally.
    // - Events are always appended in order.
    // - This method is safe to call repeatedly while recording is active.
    void AppendEvent(RecordingEventType type,
                     nlohmann::json payload);

 private:
    bool active_ = false;

    std::filesystem::path filePath_;
    nlohmann::json recordingJson_;
    uint32_t nextIndex_ = 0;
    std::chrono::steady_clock::time_point startTime_;
    const StudioSolution& solution_;

    void FlushToDisk();
};

}   // namespace webweaver::studio

#endif  // RECORDING_RECORDINGSESSION_H_
