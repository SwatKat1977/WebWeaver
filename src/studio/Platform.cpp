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
#include "Platform.h"

namespace webweaver::studio {

Platform GetCurrentPlatform()
{
#ifdef WEBWEAVER_PLATFORM_WIN64
    return Platform::Win64;
#elif defined(WEBWEAVER_PLATFORM_MACOS)
    return Platform::MacOS;
#elif defined(WEBWEAVER_PLATFORM_LINUX)
    return Platform::Linux;
#else
    return Platform::Unknown;
#endif
}

std::string PlatformToString(Platform platform) {
    switch (platform) {
        case Platform::Win64: return "WIN64";
        case Platform::Linux: return "Linux";
        case Platform::MacOS: return "MacOS";
        default: return "Unknown";
    }
}

}   // namespace webweaver::studio
