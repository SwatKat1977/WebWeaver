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

#ifndef STUDIOSOLUTION_H_
#define STUDIOSOLUTION_H_
#include <string>
#include <utility>

namespace webweaver::studio {

struct StudioSolution {
    std::string solutionName;
    std::string solutionDirectory;
    bool createDirectoryForSolution;
    std::string baseUrl;
    std::string selectedBrowser;

    StudioSolution(std::string name,
                   std::string solutionDir,
                   bool createSolutionDir,
                   std::string url,
                   std::string browser)
        : solutionName(std::move(name)),
          solutionDirectory(std::move(solutionDir)),
          createDirectoryForSolution(createSolutionDir),
          baseUrl(std::move(url)),
          selectedBrowser(std::move(browser)) {
    }
};

}   // namespace webweaver::studio

#endif  // STUDIOSOLUTION_H_
