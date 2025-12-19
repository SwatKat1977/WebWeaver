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
#include <wx/stdpaths.h>
#include <fstream>
#include <string>
#include <nlohmann/json.hpp>
#include "RecentSolutionsManager.h"

namespace webweaver::studio {

void RecentSolutionsManager::Load() {
    recent_.clear();

    std::ifstream in(GetStoragePath());
    if (!in.is_open())
        return;

    nlohmann::json j;
    in >> j;

    if (!j.contains("recentSolutions"))
        return;

    for (const auto& entry : j["recentSolutions"]) {
        recent_.emplace_back(entry.get<std::string>());
    }
}

void RecentSolutionsManager::Save() const {
    nlohmann::json j;
    j["version"] = 1;

    for (const auto& p : recent_)
        j["recentSolutions"].push_back(p.string());

    std::filesystem::create_directories(
        GetStoragePath().parent_path());

    std::ofstream out(GetStoragePath());
    out << j.dump(2);
}

void RecentSolutionsManager::AddSolution(
    const std::filesystem::path& path) {
    auto it = std::find(recent_.begin(), recent_.end(), path);
    if (it != recent_.end())
        recent_.erase(it);

    recent_.insert(recent_.begin(), path);

    if (recent_.size() > kMaxRecent)
        recent_.resize(kMaxRecent);

    Save();
}

std::filesystem::path  RecentSolutionsManager::GetStoragePath() const {
    wxString baseDir = wxStandardPaths::Get().GetUserConfigDir();
    return std::filesystem::path(baseDir.ToStdString())
        / "webweaver"
        / "recent_solutions.json";
}

}   // namespace webweaver::studio
