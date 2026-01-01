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
#include "BrowserLaunchOptions.h"

namespace webweaver::studio {

nlohmann::json BrowserLaunchOptions::ToJson() const {
    nlohmann::json j;

    j["privateMode"] = privateMode;
    j["disableExtensions"] = disableExtensions;
    j["disableNotifications"] = disableNotifications;
    j["ignoreCertificateErrors"] = ignoreCertificateErrors;
    j["maximised"] = maximised;

    if (userAgent) {
        j["userAgent"] = *userAgent;
    }

    if (windowSize) {
        j["windowSize"] = {
            { "width", windowSize->width },
            { "height", windowSize->height }
        };
    }

    return j;
}

BrowserLaunchOptions BrowserLaunchOptions::FromJson(const nlohmann::json& j) {
    BrowserLaunchOptions opts;

    if (!j.is_object()) {
        // No launcher options, use defaults.
        return opts;
    }

    opts.privateMode =
        j.value("privateMode", opts.privateMode);

    opts.disableExtensions =
        j.value("disableExtensions", opts.disableExtensions);

    opts.disableNotifications =
        j.value("disableNotifications", opts.disableNotifications);

    opts.ignoreCertificateErrors =
        j.value("ignoreCertificateErrors",
                opts.ignoreCertificateErrors);

    opts.maximised =
        j.value("maximised", opts.maximised);

    if (j.contains("userAgent") && j["userAgent"].is_string()) {
        opts.userAgent = j["userAgent"].get<std::string>();
    }

    if (j.contains("windowSize") && j["windowSize"].is_object()) {
        const auto& ws = j["windowSize"];
        if (ws.contains("width") && ws.contains("height")) {
            opts.windowSize = WindowSize{
                ws["width"].get<uint32_t>(),
                ws["height"].get<uint32_t>()
            };
        }
    }

    return opts;
}

}   // namespace webweaver::studio
