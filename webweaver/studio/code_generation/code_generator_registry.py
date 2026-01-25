"""
This source file is part of Web Weaver
For the latest info, see https://github.com/SwatKat1977/WebWeaver

Copyright 2025-2026 Webweaver Development Team

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
import importlib.util
from logging import Logger
import sys
from pathlib import Path
from typing import List
from code_generation.base_code_generator import BaseCodeGenerator


class CodeGeneratorRegistry:
    """
    Discovers and loads code generator plugins from a directory.
    """

    def __init__(self, plugin_dir: Path, logger: Logger):
        self._plugin_dir: Path = plugin_dir
        self._generators: List[BaseCodeGenerator] = []
        self._logger = logger.getChild(__name__)

    def load(self) -> None:
        """
        (Re)load all generators from disk.
        """
        self._generators.clear()

        if not self._plugin_dir.exists():
            return

        for file in self._plugin_dir.glob("*.py"):
            if file.name.startswith("_"):
                continue

            try:
                gen = self._load_from_file(file)
                if gen:
                    self._generators.append(gen)
            except Exception as e:
                self._logger.info(f"[CodeGen] Failed to load %s: %s", file, e)

    def get_generators(self) -> List[BaseCodeGenerator]:
        return list(self._generators)

    def _load_from_file(self, path: Path) -> BaseCodeGenerator | None:
        module_name = f"webweaver_codegen_{path.stem}"

        spec = importlib.util.spec_from_file_location(module_name, path)
        if spec is None or spec.loader is None:
            return None

        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)

        # Convention: plugin must expose GENERATOR = instance
        gen = getattr(module, "GENERATOR", None)

        if gen is None:
            return None

        if not isinstance(gen, BaseCodeGenerator):
            raise TypeError("GENERATOR is not a CodeGenerator")

        return gen
