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
#ifndef BROWSERLAUNC__HOPTIONS_H_
#define BROWSERLAUNC__HOPTIONS_H_
#include <unordered_map>
#include "BrowserController.h"
#include "BrowserType.h"
#include "WebDriverOptionParameter.h"

namespace webweaver::studio {

class SeleniumOptions {
public:
    void addArgument(const std::string& arg);

    void addExperimentalOption(
        const std::string& name,
        const std::unordered_map<std::string, int>& prefs
    );

    void setPreference(const std::string& key, int value);
};

static void applyOption(
    const WebDriverOptionParameter& param,
    BrowserType browser,
    SeleniumOptions& options,
    std::unordered_map<std::string, int>& chromiumPrefs);

}   // namespace webweaver::studio

#endif  // WEBDRIVEROPTIONPA__RAMETER_H_
