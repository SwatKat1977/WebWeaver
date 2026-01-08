"""
This source file is part of Web Weaver
For the latest info, see https://github.com/SwatKat1977/WebWeaver

Copyright 2025-2026 Webweaver Development Team

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


def normalise_classes(raw_classes: list) -> list[dict]:
    """
    Normalize and merge class entries.

    Input can contain:
      - strings: "MyTestClass"
      - dicts: { "name": "...", "methods": { "include": [...], "exclude": [...] } }

    Output:
      - list of dicts: { "name": str, "methods": { "include": list, "exclude": list } }

    Rules:
      - Merge entries by class name
      - Merge include/exclude lists
      - Remove duplicates, preserve order
      - Preserve first-seen class order
    """

    merged: dict[str, dict] = {}
    order: list[str] = []

    def extend_unique(dst_list: list, src_list: list):
        seen = set(dst_list)
        for item in src_list:
            if item not in seen:
                dst_list.append(item)
                seen.add(item)

    for cls in raw_classes:
        if isinstance(cls, str):
            name = cls
            methods = {"include": [], "exclude": []}
        else:
            name = cls["name"]
            raw_methods = cls.get("methods", {})

            include = raw_methods.get("include", [])
            exclude = raw_methods.get("exclude", [])

            if isinstance(include, str):
                include = [include]
            if isinstance(exclude, str):
                exclude = [exclude]

            methods = {"include": include, "exclude": exclude}

        if name not in merged:
            merged[name] = {
                "name": name,
                "methods": {"include": [], "exclude": []},
            }
            order.append(name)

        extend_unique(merged[name]["methods"]["include"], methods["include"])
        extend_unique(merged[name]["methods"]["exclude"], methods["exclude"])

    return [merged[name] for name in order]
