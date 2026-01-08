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


def normalise_suite(data: dict,
                    default_suite_threads: int,
                    default_test_threads: int) -> dict:
    """
    Normalize a parsed and schema-validated test suite definition.

    This function applies all suite- and test-level business rules and
    defaulting logic, transforming the raw suite dictionary into a fully
    normalized form that the executor can rely on.

    The following rules are applied:

    Suite-level:
      - If 'suite.parallel' is missing, it defaults to "none".
      - If 'suite.thread_count' is missing, it defaults to
        'default_suite_threads'.

    Test-level:
      - If 'test.parallel' is missing, it inherits from 'suite.parallel'.
      - If 'test.parallel' == "none", then 'test.thread_count' is forced to 1.
      - Otherwise, if 'test.thread_count' is missing, it defaults to:
            - 'suite.thread_count' if present
            - otherwise 'default_test_threads'

    Classes:
      - Each test's 'classes' list is normalized via 'normalise_classes':
            - class entries are merged by name
            - method include/exclude lists are defaulted and deduplicated
            - first-seen class order is preserved

    The input dictionary is modified in-place and also returned.

    Args:
        data (dict):
            A parsed and schema-validated suite definition.

        default_suite_threads (int):
            Default thread count for the suite if not specified.

        default_test_threads (int):
            Default thread count for tests if not specified.

    Returns:
        dict:
            The normalized suite definition dictionary.
    """
    suite = data["suite"]

    # Suite-level defaults
    suite.setdefault("parallel", "none")
    suite.setdefault("thread_count", default_suite_threads)

    for test in data["tests"]:
        # Inherit parallel from suite if not specified
        test["parallel"] = test.get("parallel", suite.get("parallel", "none"))

        # Compute thread_count with sensible defaults
        if test["parallel"] == "none":
            test["thread_count"] = 1
        else:
            test.setdefault(
                "thread_count",
                suite.get("thread_count", default_test_threads)
            )

        # Normalise the test classes
        test["classes"] = normalise_classes(test["classes"])

    return data
