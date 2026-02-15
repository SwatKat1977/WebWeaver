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
import typing
from .base_code_generator import BaseCodeGenerator
from .base_code_generator_settings import BaseCodeGeneratorSettings
from .code_generator_entry import CodeGeneratorRegistryEntry


class CodeGeneratorRegistry:
    """
    Discovers and loads code generator plugins from a directory.
    """

    def __init__(self, plugin_dir: Path, logger: Logger):
        self._plugin_dir: Path = plugin_dir
        self._generators: typing.List[CodeGeneratorRegistryEntry] = []
        self._logger = logger.getChild(__name__)

    def load(self) -> None:
        """
        (Re)load all generators from disk.
        """
        # pylint: disable=broad-exception-caught

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
                self._logger.info("[CodeGen] Failed to load %s: %s", file, e)

    def get_generators(self) -> typing.List[CodeGeneratorRegistryEntry]:
        """
        Return the list of currently loaded code generator plugins.

        This method returns a shallow copy of the internally registered
        generator list to prevent external callers from mutating the manager's
        internal state.

        The returned generators are guaranteed to be instances of
        BaseCodeGenerator and represent successfully loaded and validated
        plugins.

        :return: A list of loaded BaseCodeGenerator instances.
        """
        return list(self._generators)

    def _load_from_file(self, path: Path) -> (
            typing.Optional)[CodeGeneratorRegistryEntry]:
        """
        Load a code generator plugin from a Python source file.

        This method dynamically imports the module at the given path using a
        unique, generated module name to avoid collisions in sys.modules.

        Plugin contract:
            - The module must define a top-level attribute named `GENERATOR`
            - `GENERATOR` must be an instance of BaseCodeGenerator

        If the module cannot be imported, does not define GENERATOR, or does
        not conform to the expected type, the plugin is rejected.

        This method does not register the generator; it only loads and
        validates it.

        :param path: Path to the Python file containing the generator plugin.
        :return: The loaded BaseCodeGenerator instance, or None if the file
                 could not be loaded or does not define a valid plugin.
        :raises TypeError: If the module defines GENERATOR but it is not a
                           BaseCodeGenerator instance.
        """
        module_name = f"webweaver_codegen_{path.stem}"

        spec = importlib.util.spec_from_file_location(module_name, path)
        if spec is None or spec.loader is None:
            return None

        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)

        gen_cls = getattr(module, "GENERATOR_CLASS", None)
        settings_cls = getattr(module, "SETTINGS_CLASS", None)

        if gen_cls is None or settings_cls is None:
            return None

        if not issubclass(gen_cls, BaseCodeGenerator):
            raise TypeError("GENERATOR_CLASS is not a BaseCodeGenerator subclass")

        if not issubclass(settings_cls, BaseCodeGeneratorSettings):
            raise TypeError("SETTINGS_CLASS is not a BaseCodeGeneratorSettings subclass")

        return CodeGeneratorRegistryEntry(gen_cls, settings_cls)
