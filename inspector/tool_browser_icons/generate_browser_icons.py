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
import base64
import textwrap

chrome_header: str = """
# -----------------------
# Google Chrome Browser Icon (Base64)
# -----------------------
"""
chrome_variable = 'CHROME_BROWSER_ICON = b"""\n'

ms_edge_header: str = """
# -----------------------
# Microsoft Edge Browser Icon (Base64)
# -----------------------
"""
ms_edge_variable = 'MICROSOFT_EDGE_BROWSER_ICON = b"""\n'

firefox_header: str = """
# -----------------------
# Firefox Browser Icon (Base64)
# -----------------------
"""
firefox_variable = 'FIREFOX_BROWSER_ICON = b"""\n'

variable_close = '\n"""\n\n'

with open("Google_Chrome.png", "rb") as f:
    chrome_img = base64.b64encode(f.read()).decode("ascii")

with open("Firefox_logo.png", "rb") as f:
    firefox_img = base64.b64encode(f.read()).decode("ascii")

with open("Microsoft_Edge.png", "rb") as f:
    edge_img = base64.b64encode(f.read()).decode("ascii")

with open("browser_icons.py", "w", encoding="utf-8") as output_py:
    output_py.write(chrome_header)
    output_py.write(chrome_variable)
    output_py.write("\n".join(textwrap.wrap(chrome_img, width=80)))
    output_py.write(variable_close)

    output_py.write(firefox_header)
    output_py.write(firefox_variable)
    output_py.write("\n".join(textwrap.wrap(firefox_img, width=80)))
    output_py.write(variable_close)

    output_py.write(ms_edge_header)
    output_py.write(ms_edge_variable)
    output_py.write("\n".join(textwrap.wrap(edge_img, width=80)))
    output_py.write(variable_close)
