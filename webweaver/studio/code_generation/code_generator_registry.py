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
    Registry responsible for discovering and loading code generator plugins.

    The registry scans a given plugin directory, loads available generator
    implementations, and stores them as `CodeGeneratorRegistryEntry` instances.
    It also provides access to the configured plugin directory.

    Each registry instance is scoped to a single plugin directory.
    """

    def __init__(self, plugin_dir: Path, logger: Logger):
        """Initialise a new CodeGeneratorRegistry.

        Args:
            plugin_dir (Path): Path to the directory containing generator plugins.
            logger (Logger): Base logger instance used for logging registry
                activity. A child logger scoped to this module is created.
        """
        self._plugin_dir: Path = plugin_dir
        self._generators: typing.List[CodeGeneratorRegistryEntry] = []
        self._logger = logger.getChild(__name__)

    @property
    def plugin_dir(self) -> Path:
        """Return the currently configured plugin directory.

        Returns:
            Path: The path representing the plugin directory.
        """
        return self._plugin_dir

    @plugin_dir.setter
    def plugin_dir(self, plugin_dir: Path):
        """Update the plugin directory used for discovering plugins.

        Changing this value does not automatically reload or rediscover
        generators. The caller is responsible for triggering any required
        refresh logic after updating the directory.

        Args:
            plugin_dir (Path): The new plugin directory path.
        """
        self._plugin_dir = plugin_dir = plugin_dir

    def load(self) -> None:
        """Load or reload all generator plugins from the configured directory.

        This method clears the current registry and scans the plugin directory
        for Python files. Each valid plugin module is imported and validated
        before being registered.

        Files beginning with "_" are ignored.

        If the plugin directory does not exist, the registry remains empty.

        Any exceptions raised during plugin loading are caught and logged,
        allowing the registry to continue processing remaining files.
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

        Returns:
            List[CodeGeneratorRegistryEntry]: The loaded generator entries.
        """
        return list(self._generators)

    def _load_from_file(self, path: Path) -> \
            typing.Optional[CodeGeneratorRegistryEntry]:
        """Load and validate a code generator plugin from a Python file.

        The module is dynamically imported using a unique module name to avoid
        collisions in ``sys.modules``.

        Plugin contract:
            - The module must define a top-level ``GENERATOR_CLASS`` attribute.
            - The module must define a top-level ``SETTINGS_CLASS`` attribute.
            - ``GENERATOR_CLASS`` must be a subclass of BaseCodeGenerator.
            - ``SETTINGS_CLASS`` must be a subclass of BaseCodeGeneratorSettings.

        This method performs loading and validation only. It does not register
        the generator in the registry.

        Args:
            path (Path): Path to the Python file containing the generator plugin.

        Returns:
            Optional[CodeGeneratorRegistryEntry]: A registry entry containing
            the generator and settings classes if valid, otherwise None.

        Raises:
            TypeError: If GENERATOR_CLASS is not a BaseCodeGenerator subclass.
            TypeError: If SETTINGS_CLASS is not a
                BaseCodeGeneratorSettings subclass.
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
