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
#include <random>
#include <sstream>
#include <iomanip>
#include "UUID.h"

namespace webweaver::studio {


std::string GenerateUuidV4() {
    static thread_local std::mt19937_64 rng { std::random_device {}() };

    std::uniform_int_distribution<uint64_t> dist;

    uint64_t a = dist(rng);
    uint64_t b = dist(rng);

    // Set version (4) and variant (RFC 4122)
    a = (a & 0xFFFFFFFFFFFF0FFFULL) | 0x0000000000004000ULL;
    b = (b & 0x3FFFFFFFFFFFFFFFULL) | 0x8000000000000000ULL;

    std::ostringstream ss;
    ss << std::hex << std::setfill('0')
       << std::setw(8) << (a >> 32)
       << "-"
       << std::setw(4) << ((a >> 16) & 0xFFFF)
       << "-"
       << std::setw(4) << (a & 0xFFFF)
       << "-"
       << std::setw(4) << (b >> 48)
       << "-"
       << std::setw(12) << (b & 0xFFFFFFFFFFFFULL);

    return ss.str();
}

}   // namespace webweaver::studio
