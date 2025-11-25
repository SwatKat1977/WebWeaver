/*
This source file is part of Web Weaver
For the latest info, see https ://github.com/SwatKat1977/WebWeaver

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
#ifndef SUITEPARSER_H_
#define SUITEPARSER_H_
#include <string>
#include <jsoncons/json.hpp>
#include "nlohmann/json.hpp"

namespace WebWeaver { namespace Executor {

class SuiteParser {
 public:
    static constexpr int DEFAULT_SUITE_THREAD_COUNT = 10;
    static constexpr int DEFAULT_TEST_THREAD_COUNT = 10;

    explicit SuiteParser(const std::string& schemaFile);

    nlohmann::json LoadSuite(const std::string& filePath);

 private:
    nlohmann::json suiteSchema_;

    nlohmann::json Normalise(nlohmann::json data);
    jsoncons::json ConvertFromNlohmann(const nlohmann::json& j);
};

}   // namespace Executor
}   // namespace WebWeaver

#endif  // SUITEPARSER_H_
