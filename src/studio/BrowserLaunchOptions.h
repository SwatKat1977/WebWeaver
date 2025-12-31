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
#ifndef BROWSERLAUNCHOPTIONS_H_
#define BROWSERLAUNCHOPTIONS_H_
#include <cstdint>
#include <string>
#include <optional>
#include <nlohmann/json.hpp>

namespace webweaver::studio {

struct WindowSize {
    uint32_t width = 0;
    uint32_t height = 0;
};

struct BrowserLaunchOptions {
    bool privateMode = true;
    bool disableExtensions = true;
    bool disableNotifications = true;
    bool ignoreCertificateErrors = false;

    std::optional<std::string> userAgent;
    std::optional<WindowSize> windowSize;
    bool maximised = false;

    nlohmann::json ToJson() const;

    static BrowserLaunchOptions FromJson(const nlohmann::json& j);
};

}   // namespace webweaver::studio

#endif  // BROWSERLAUNCHOPTIONS_H_
