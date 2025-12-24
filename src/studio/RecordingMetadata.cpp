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
#include <fstream>
#include <nlohmann/json.hpp>
#include "RecordingMetadata.h"

namespace webweaver::studio {

RecordingLoadResult RecordingMetadata::FromFile(
    const std::filesystem::path& wwrecFile) {
    if (!std::filesystem::exists(wwrecFile)) {
        return { {}, RecordingLoadError::FileNotFound };
    }

    nlohmann::json json;

    try {
        std::ifstream in(wwrecFile);
        in >> json;
    } catch (...) {
        return { {}, RecordingLoadError::FileMalformed };
    }

    if (!json.contains("recording") || !json["recording"].is_object()) {
        return { {}, RecordingLoadError::MissingRecordingObject };
    }

    const auto& r = json["recording"];

    if (!r.contains("id") || !r.contains("name") || !r.contains("createdAt")) {
        return { {}, RecordingLoadError::MissingRequiredField };
    }

    RecordingMetadata meta;
    meta.id = r["id"].get<std::string>();
    meta.name = r["name"].get<std::string>();
    meta.filePath = wwrecFile;

    meta.createdAt =
        std::chrono::system_clock::from_time_t(
            std::time(nullptr)); // placeholder for now

    return { meta, RecordingLoadError::None };
}

std::string RecordingLoadErrorToStr(RecordingLoadError error) {
    switch (error) {
    case RecordingLoadError::FileMalformed:
        return "Recording metadata is malformed.";

    case RecordingLoadError::MissingRecordingObject:
        return "Recording metadata missing 'recording' JSON field.";

    case RecordingLoadError::MissingRequiredField:
        return "Recording metadata missing required JSON field.";

    case RecordingLoadError::UnsupportedVersion:
        return "Recording metadata has unsupported version.";

    case RecordingLoadError::FileNotFound:
        return "Recording metadata file was not found.";

    default:
        return {};
    }
}

}   // namespace webweaver::studio
