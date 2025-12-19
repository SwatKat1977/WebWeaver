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
#include "StudioSolution.h"

namespace webweaver::studio {

constexpr int JSON_VERSION = 1;

nlohmann::json StudioSolution::ToJson() const {
    return {
        { "version", JSON_VERSION },
        { "solution", {
            { "SolutionName", solutionName },
            { "solutionDirectory", solutionDirectory },
            { "solutionDirectoryCreated", createDirectoryForSolution },
            { "baseUrl", baseUrl },
            { "browser", selectedBrowser }
        }}
    };
}

StudioSolution StudioSolution::FromJson(const nlohmann::json& j) {
    const auto& s = j.at("solution");

    return StudioSolution{
        s.at("SolutionName").get<std::string>(),
        s.at("solutionDirectory").get<std::string>(),
        s.at("solutionDirectoryCreated").get<bool>(),
        s.at("baseUrl").get<std::string>(),
        s.at("browser").get<std::string>()
    };
}

}   // namespace webweaver::studio
