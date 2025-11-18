"""
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
"""

# Semantic version components
MAJOR = 0
MINOR = 5
PATCH = 0

# e.g. "alpha", "beta", "rc1", or None
PRE_RELEASE = "Alpha #1"

# Version tuple for comparisons
VERSION = (MAJOR, MINOR, PATCH, PRE_RELEASE)

# Construct the string representation
__version__ = f"V{MAJOR}.{MINOR}.{PATCH}"

if PRE_RELEASE:
    __version__ += f"-{PRE_RELEASE}"