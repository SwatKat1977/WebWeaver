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

stop_button_header: str = """
# -----------------------
# Stop Button Icon (Base64)
# -----------------------
"""
stop_button_variable = 'STOP_BUTTON_ICON = b"""\n'

inspect_button_header: str = """
# -----------------------
# Inspect Button Icon (Base64)
# -----------------------
"""
inspect_button_variable = 'INSPECT_BUTTON_ICON = b"""\n'

open_button_header: str = """
# -----------------------
# Open Button Icon (Base64)
# -----------------------
"""
open_button_variable = 'OPEN_BUTTON_ICON = b"""\n'

new_project_button_header: str = """
# -----------------------
# New Project Button Icon (Base64)
# -----------------------
"""
new_project_button_variable = 'NEW_PROJECT_BUTTON_ICON = b"""\n'

save_project_button_header: str = """
# -----------------------
# Save Project Button Icon (Base64)
# -----------------------
"""
save_project_button_variable = 'SAVE_PROJECT_BUTTON_ICON = b"""\n'

variable_close = '\n"""\n\n'

print("Reading 'Record button'")
with open("rec-button.png", "rb") as f:
    rec_button_img = base64.b64encode(f.read()).decode("ascii")

print("Reading 'Pause button'")
with open("pause-button.png", "rb") as f:
    pause_button_img = base64.b64encode(f.read()).decode("ascii")

print("Reading 'Stop button'")
with open("stop-button.png", "rb") as f:
    stop_button_img = base64.b64encode(f.read()).decode("ascii")

print("Reading 'Inspect button'")
with open("inspect-button.png", "rb") as f:
    inspect_button_img = base64.b64encode(f.read()).decode("ascii")

print("Reading 'Open button'")
with open("open-button.png", "rb") as f:
    open_button_img = base64.b64encode(f.read()).decode("ascii")

print("Reading 'New Project button'")
with open("new-project-button.png", "rb") as f:
    new_project_button_img = base64.b64encode(f.read()).decode("ascii")

print("Reading 'Save Project button'")
with open("save-button.png", "rb") as f:
    save_project_button_img = base64.b64encode(f.read()).decode("ascii")

with open("toolbar_icons.py", "w", encoding="utf-8") as output_py:
    output_py.write(rec_button_header)
    output_py.write(record_button_variable)
    output_py.write("\n".join(textwrap.wrap(rec_button_img, width=80)))
    output_py.write(variable_close)

    output_py.write(pause_button_header)
    output_py.write(pause_button_variable)
    output_py.write("\n".join(textwrap.wrap(pause_button_img, width=80)))
    output_py.write(variable_close)

    output_py.write(inspect_button_header)
    output_py.write(inspect_button_variable)
    output_py.write("\n".join(textwrap.wrap(inspect_button_img, width=80)))
    output_py.write(variable_close)

    output_py.write(open_button_header)
    output_py.write(open_button_variable)
    output_py.write("\n".join(textwrap.wrap(open_button_img, width=80)))
    output_py.write(variable_close)

    output_py.write(new_project_button_header)
    output_py.write(new_project_button_variable)
    output_py.write("\n".join(textwrap.wrap(new_project_button_img, width=80)))
    output_py.write(variable_close)

    output_py.write(stop_button_header)
    output_py.write(stop_button_variable)
    output_py.write("\n".join(textwrap.wrap(stop_button_img, width=80)))
    output_py.write(variable_close)

    output_py.write(save_project_button_header)
    output_py.write(save_project_button_variable)
    output_py.write("\n".join(textwrap.wrap(save_project_button_img, width=80)))
    output_py.write(variable_close)
