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
#include <wx/wx.h>
#include <fstream>
#include "StudioSolution.h"

namespace webweaver::studio {

constexpr int JSON_VERSION = 1;

const char PAGES_DIRECTORY[] = "pages";
const char SCRIPTS_DIRECTORY[] = "scripts";
const char RECORDINGS_DIRECTORY[] = "recordings";

nlohmann::json StudioSolution::ToJson() const {
    return {
        { "version", JSON_VERSION },
        { "solution", {
            { "solutionName", solutionName },
            { "solutionDirectory", solutionDirectory },
            { "solutionDirectoryCreated", createDirectoryForSolution },
            { "baseUrl", baseUrl },
            { "browser", selectedBrowser }
        }}
    };
}

SolutionLoadResult StudioSolution::FromJson(const nlohmann::json& rawJSON) {
    if (!rawJSON.is_object())
        return { {}, SolutionLoadError::FileMalformed};

    if (!rawJSON.contains("version"))
        return { {}, SolutionLoadError::MissingVersion};

    if (!rawJSON["version"].is_number_integer())
        return { {}, SolutionLoadError::FileMalformed};

    int version = rawJSON["version"].get<int>();
    if (version != 1)
        return { {}, SolutionLoadError::UnsupportedVersion };

    if (!rawJSON.contains("solution") ||
        !rawJSON["solution"].is_object())
        return { {}, SolutionLoadError::MissingSolutionObject};

    const auto& s = rawJSON["solution"];

    if (!s.contains("solutionName") ||
        !s.contains("solutionDirectory") ||
        !s.contains("solutionDirectoryCreated") ||
        !s.contains("baseUrl") ||
        !s.contains("browser"))
        return { {}, SolutionLoadError::MissingRequiredField};

    return {
        StudioSolution{
            s["solutionName"].get<std::string>(),
            s["solutionDirectory"].get<std::string>(),
            s["solutionDirectoryCreated"].get<bool>(),
            s["baseUrl"].get<std::string>(),
            s["browser"].get<std::string>()
        },
        SolutionLoadError::None
    };
}

std::filesystem::path StudioSolution::GetSolutionDirectory() const {
    std::filesystem::path dir = solutionDirectory;

    if (createDirectoryForSolution) {
        dir /= solutionName;
    }

    return dir;
}

std::filesystem::path StudioSolution::GetSolutionFilePath() const {
    return GetSolutionDirectory() / (solutionName + ".wws");
}

std::string SolutionLoadErrorToStr(SolutionLoadError error) {
    std::string message;

    switch (error) {
    case SolutionLoadError::FileMalformed:
        message = "The solution file is malformed or corrupted.";
        break;

    case SolutionLoadError::MissingVersion:
        message = "The solution file does not specify a version.";
        break;

    case SolutionLoadError::UnsupportedVersion:
        message = "This solution file was created with a newer version of "
                  "WebWeaver.";
        break;

    case SolutionLoadError::MissingSolutionObject:
        message = "The solution file is missing required data.";
        break;

    case SolutionLoadError::MissingRequiredField:
        message = "The solution file is incomplete.";
        break;

    default:
        message = "Unknown solution load error.";
        break;
    }

    return message;
}

std::filesystem::path StudioSolution::GetPagesDirectory() const {
    return GetSolutionDirectory() / PAGES_DIRECTORY;
}

std::filesystem::path StudioSolution::GetScriptsDirectory() const {
    return GetSolutionDirectory() / SCRIPTS_DIRECTORY;
}

std::filesystem::path StudioSolution::GetRecordingsDirectory() const {
    return GetSolutionDirectory() / RECORDINGS_DIRECTORY;
}

SolutionDirectoryCreateStatus StudioSolution::EnsureDirectoryStructure() const {
    std::error_code ec;

    ec.clear();
    std::filesystem::create_directories(GetSolutionDirectory(), ec);
    if (ec) return SolutionDirectoryCreateStatus::CannotCreateRoot;

    ec.clear();
    std::filesystem::create_directories(GetPagesDirectory(), ec);
    if (ec) return SolutionDirectoryCreateStatus::CannotCreatePages;

    ec.clear();
    std::filesystem::create_directories(GetScriptsDirectory(), ec);
    if (ec) return SolutionDirectoryCreateStatus::CannotCreateScripts;

    ec.clear();
    std::filesystem::create_directories(GetRecordingsDirectory(), ec);
    if (ec) return SolutionDirectoryCreateStatus::CannotCreateRecordings;

    return SolutionDirectoryCreateStatus::None;
}

std::vector<RecordingMetadata> StudioSolution::DiscoverRecordingFiles() const {
    std::vector<RecordingMetadata> recordings;

    const auto dir = GetRecordingsDirectory();
    if (!std::filesystem::exists(dir))
        return recordings;

    for (const auto& entry : std::filesystem::directory_iterator(dir)) {
        if (!entry.is_regular_file()) {
            continue;
        }

        if (entry.path().extension() != ".wwrec") {
            continue;
        }

        auto result = RecordingMetadata::FromFile(entry.path());

        if (!result.recording) {
            wxLogWarning(
                "Skipping recording %s:\n%s",
                entry.path().string(),
                RecordingLoadErrorToStr(result.error));
            continue;
        }

        recordings.push_back(std::move(*result.recording));
    }

    return recordings;
}

std::string StudioSolution::GenerateNextRecordingName() const {
    auto recordings = DiscoverRecordingFiles();
    return "Recording " + std::to_string(recordings.size() + 1);
}

std::string SolutionDirectoryErrorToStr(SolutionDirectoryCreateStatus err) {
    switch (err) {
    case SolutionDirectoryCreateStatus::CannotCreateRoot:
        return "Unable to create the solution directory.";

    case SolutionDirectoryCreateStatus::CannotCreatePages:
        return "Unable to create the Pages folder.";

    case SolutionDirectoryCreateStatus::CannotCreateScripts:
        return "Unable to create the Scripts folder.";

    case SolutionDirectoryCreateStatus::CannotCreateRecordings:
        return "Unable to create the Recordings folder.";

    default:
        return {};
    }
}

}   // namespace webweaver::studio
