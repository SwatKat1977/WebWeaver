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
#include <string>
#include "FilesystemUtils.h"

namespace webweaver::studio {

bool isdDirectoryWritable(const std::filesystem::path& dir) {
    if (!std::filesystem::exists(dir) || !std::filesystem::is_directory(dir)) {
        return false;
    }

    // Try creating a temporary file inside the directory
    std::filesystem::path testFile = dir / ".write_test_tmp";

    std::ofstream ofs(testFile.string(), std::ios::out | std::ios::trunc);
    if (!ofs.is_open())
        return false;

    ofs.close();
    std::filesystem::remove(testFile);

    return true;
}

}   // namespace webweaver::studio


