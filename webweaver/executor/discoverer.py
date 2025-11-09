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
import importlib.util
import inspect
import logging
import pathlib
from typing import List
from executor.test_listener import TestListener


def discover_listeners(
        logger: logging.Logger,
        search_path: str | pathlib.Path = ".") -> List[TestListener]:
    """
    Discover *global* TestListener subclasses from listener_*.py modules
    within the given path. These apply to all tests automatically.

    Returns a list of instantiated listener objects.
    """
    search_path = pathlib.Path(search_path).resolve()
    found_listeners = []

    logger.debug("Scanning for listeners in %s", search_path)

    for file in search_path.rglob("listener_*.py"):
        # Skip hidden/system dirs
        if any(part.startswith(".") or
               part in ("__pycache__",
                        "venv",
                        ".venv") for part in file.parts):
            continue

        logger.debug("Importing listener module: %s", file)
        spec = importlib.util.spec_from_file_location(file.stem, file)
        module = importlib.util.module_from_spec(spec)

        try:
            spec.loader.exec_module(module)
        except Exception as e:
            print(f"[WARN] Could not import {file}: {e}")
            continue

        for _, cls in inspect.getmembers(module, inspect.isclass):
            if issubclass(cls, TestListener) and cls is not TestListener:
                print(f"[FOUND] Listener class: {cls.__name__}")
                found_listeners.append(cls())

    # Deduplicate by listener class type
    unique = {type(l).__name__: l for l in found_listeners}
    print("[DEBUG] Discovered listener instances:")
    for l in unique.values():
        print(f"  -> {type(l).__name__} {id(l)}")

    return list(unique.values())


def import_test_modules(search_path: str | pathlib.Path = ".") -> List[str]:
    """Import all test modules matching test_*.py."""
    search_path = pathlib.Path(search_path).resolve()
    imported = []

    print(f"[INFO] Importing test modules from {search_path}")

    for file in search_path.rglob("test_*.py"):
        if any(part.startswith(".") or
               part in ("__pycache__",
                        "venv",
                        ".venv") for part in file.parts):
            continue

        print(f"[DEBUG] Importing test module: {file}")
        spec = importlib.util.spec_from_file_location(file.stem, file)
        module = importlib.util.module_from_spec(spec)

        try:
            spec.loader.exec_module(module)
            imported.append(file.stem)
        except Exception as e:
            print(f"[WARN] Failed to import {file}: {e}")
            continue

    return imported
