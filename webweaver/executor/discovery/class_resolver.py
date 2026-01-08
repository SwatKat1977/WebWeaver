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
import importlib


class ClassResolutionError(Exception):
    """ Class resolution error """
    pass


def resolve_class(dotted_path: str):
    """
    Resolve and return a class object from a dotted path string.

    Example:
        "automation.portal.tests.proof_of_concept.TestPortal"
    """

    try:
        module_name, class_name = dotted_path.rsplit(".", 1)

    except ValueError as ex:
        raise ClassResolutionError(
            f"Invalid class path '{dotted_path}'. Expected format: "
            "module.ClassName") from ex

    try:
        module = importlib.import_module(module_name)
    except Exception as ex:
        raise ClassResolutionError(
            f"Failed to import module '{module_name}' for "
            "class '{dotted_path}'") from ex

    try:
        cls = getattr(module, class_name)
    except AttributeError as ex:
        raise ClassResolutionError(
            f"Module '{module_name}' does not define a class"
            "named '{class_name}'") from ex

    return cls
