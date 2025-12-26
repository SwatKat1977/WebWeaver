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
#ifndef SOLUTIONEXPLORERNODEDATA_H_
#define SOLUTIONEXPLORERNODEDATA_H_
#include <wx/wx.h>

namespace webweaver::studio {

enum class ExplorerNodeType {
    SolutionRoot,
    FolderPages,
    FolderScripts,
    FolderRecordings,
    RecordingItem
};

class ExplorerNodeData : public wxTreeItemData {
 public:
    explicit ExplorerNodeData(ExplorerNodeType type,
                              std::filesystem::path path)
        : type_(type), path_(std::move(path)) {}

    ExplorerNodeType GetType() const { return type_; }

    const std::filesystem::path& GetPath() const { return path_; }

 private:
    ExplorerNodeType type_;
    std::filesystem::path path_;
};

}   // namespace webweaver::studio

#endif  // SOLUTIONEXPLORERNODEDATA_H_
