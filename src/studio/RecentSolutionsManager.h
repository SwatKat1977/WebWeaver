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
#ifndef RECENTSOLUTIONSMANAGER_H_
#define RECENTSOLUTIONSMANAGER_H_
#include <filesystem>
#include <vector>

namespace webweaver::studio {

class RecentSolutionsManager {
 public:
    void Load();
    void Save() const;

    void AddSolution(const std::filesystem::path& solutionFile);

    const std::vector<std::filesystem::path>& GetSolutions() const {
        return recent_;
    }

 private:
    std::vector<std::filesystem::path> recent_;
    static constexpr size_t kMaxRecent = 10;

    std::filesystem::path GetStoragePath() const;
};

}   // namespace webweaver::studio

#endif  // RECENTSOLUTIONSMANAGER_H_
