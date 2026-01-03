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
from png_to_header import png_to_header

png_to_header("browserIcons/Chromium_Logo.png",
    "browserIcons/browser_chromium_logo.py",
    "browser_chromium_logo")

png_to_header("browserIcons/Firefox_Logo.png",
              "browserIcons/browser_firefox_logo.py",
    "browser_firefox_logo")

png_to_header("browserIcons/Google_Chrome.png",
    "browserIcons/browser_google_chrome_logo.py",
    "browser_google_chrome_logo")

png_to_header("browserIcons/Microsoft_Edge.png",
    "browserIcons/browser_microsoft_edge_logo.py",
    "browser_microsoft_edge_logo")
