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
from pathlib import Path
from datetime import datetime

header_block = f"""\
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
"""

def png_to_header(png_path: str, header_path: str, var_name: str):
    input_png = Path(png_path)
    data = input_png.read_bytes()

    out_path = Path(header_path)
    var_upper = var_name.upper()

    with out_path.open("w", encoding="ascii") as out:
        # Write header block
        out.write(header_block)
        out.write("\n")

        # Write array
        out.write(f"static const unsigned char {var_upper}[] = {{\n    ")

        for i, b in enumerate(data):
            out.write(f"0x{b:02X}, ")
            if (i + 1) % 12 == 0:
                out.write("\n    ")

        out.write("\n};\n")
        out.write(f"static const unsigned int {var_upper}_SIZE = {len(data)};\n")


png_to_header("inspect-button.png",
    "toolbar_inspect.h",
    "inspect_button_icon")

png_to_header("new-project-button.png",
    "toolbar_new_project.h",
    "inspect_new_project_icon")

png_to_header("open-button.png",
    "toolbar_open_project.h",
    "inspect_open_project_icon")

png_to_header("pause-button.png",
    "toolbar_pause_record.h",
    "pause_record_icon")

png_to_header("rec-button.png",
    "toolbar_start_record.h",
    "start_record_icon")

png_to_header("save-button.png",
    "toolbar_save_project.h",
    "save_project_icon")

png_to_header("stop-button.png",
    "toolbar_stop_record.h",
    "stop_record_icon")
