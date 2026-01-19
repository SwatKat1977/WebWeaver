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

header_block = '''\
"""This source file is part of Web Weaver
For the latest info, see https://github.com/SwatKat1977/WebWeaver

Copyright 2025-2026 SwatKat1977

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.
"""
# pylint: skip-file
'''

BYTES_PER_LINE : int = 12

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
        out.write(f"{var_upper}: bytes = bytes([\n    ")

        for i in range(0, len(data), BYTES_PER_LINE):
            chunk = data[i:i + BYTES_PER_LINE]
            line = ", ".join(f"0x{b:02X}" for b in chunk)
            out.write(f"    {line},\n")

        out.write("\n])\n")

        out.write(f"{var_upper}_SIZE: int = {len(data)}\n")
