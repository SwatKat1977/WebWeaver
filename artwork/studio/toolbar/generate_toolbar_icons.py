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


rec_button_header: str = """
# -----------------------
# Record Button Icon (Base64)
# -----------------------
"""
record_button_variable = 'RECORD_BUTTON_ICON = b"""\n'

pause_button_header: str = """
# -----------------------
# Pause Button Icon (Base64)
# -----------------------
"""
pause_button_variable = 'PAUSE_BUTTON_ICON = b"""\n'

variable_close = '\n"""\n\n'

with open("rec-button.png", "rb") as f:
    rec_button_img = base64.b64encode(f.read()).decode("ascii")

with open("pause-button.png", "rb") as f:
    pause_button_img = base64.b64encode(f.read()).decode("ascii")

with open("toolbar_icons.py", "w", encoding="utf-8") as output_py:
    output_py.write(rec_button_header)
    output_py.write(record_button_variable)
    output_py.write("\n".join(textwrap.wrap(rec_button_img, width=80)))
    output_py.write(variable_close)

    output_py.write(pause_button_header)
    output_py.write(pause_button_variable)
    output_py.write("\n".join(textwrap.wrap(pause_button_img, width=80)))
    output_py.write(variable_close)
