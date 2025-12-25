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
#ifndef RECORDINGMETADATA_H_
#define RECORDINGMETADATA_H_
#include <filesystem>
#include <string>

namespace webweaver::studio {

enum class RecordingLoadError {
    None,
    FileMalformed,
    MissingRecordingObject,
    MissingRequiredField,
    UnsupportedVersion,
    FileNotFound
};

struct RecordingLoadResult;

struct RecordingMetadata {
    std::string id;
    std::string name;
    std::filesystem::path filePath;
    std::chrono::system_clock::time_point createdAt;

    static RecordingLoadResult FromFile(const std::filesystem::path& wwrecFile);
};

struct RecordingLoadResult {
    std::optional<RecordingMetadata> recording;
    RecordingLoadError error = RecordingLoadError::None;
};

std::string RecordingLoadErrorToStr(RecordingLoadError error);

}   // namespace webweaver::studio

#endif  // RECORDINGMETADATA_H_
