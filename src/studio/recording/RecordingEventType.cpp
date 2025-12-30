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
#include "RecordingEventType.h"

namespace webweaver::studio {

RecordingEventType EventTypeFromString(const std::string& str) {
    if (str == "nav.goto")  return RecordingEventType::NavGoto;
    if (str == "dom.click") return RecordingEventType::DomClick;
    if (str == "wait")      return RecordingEventType::Wait;

    return RecordingEventType::Unknown;
}

std::string EventTypeToString(RecordingEventType type) {
    switch (type) {
        case RecordingEventType::NavGoto:  return "nav.goto";
        case RecordingEventType::DomClick: return "dom.click";
        case RecordingEventType::Wait:     return "wait";
        default:                           return "unknown";
    }
}

}   // namespace webweaver::studio
