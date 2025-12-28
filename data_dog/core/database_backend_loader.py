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
import importlib
import os
from data_dog.core.database_backend import DatabaseBackend


def load_backend(backend_name: str) -> DatabaseBackend:
    module_path = f"data_dog.plugins.{backend_name}.backend"

    actual_path: str = os.path.join("data_dog", "plugins", backend_name)

    if not os.path.isdir(actual_path):
        raise RuntimeError(f"'plugins' directory '{actual_path}' doesn't exist.")

    try:
        module = importlib.import_module(module_path)
    except ModuleNotFoundError:
        raise RuntimeError(f"Database backend '{backend_name}' not found.")

    if not hasattr(module, "create_backend"):
        raise RuntimeError(f"Backend '{backend_name}' missing create_backend().")

    backend = module.create_backend()

    if not isinstance(backend, DatabaseBackend):
        raise TypeError(f"Backend '{backend_name}' does not implement DatabaseBackend.")

    return backend

try:
    load_backend("sqlserver")

except RuntimeError as ex:
    print(ex)

