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
from typing import Type
from .base_code_generator import BaseCodeGenerator
from .base_code_generator_settings import BaseCodeGeneratorSettings


class CodeGeneratorRegistryEntry:
    """
    Represents a single entry in the code generator registry.

    Each registry entry pairs a concrete code generator class with its
    corresponding settings class, allowing them to be instantiated and
    managed together in a consistent way.
    """
    # pylint: disable=too-few-public-methods

    def __init__(self,
                 generator_cls: Type[BaseCodeGenerator],
                 settings_cls: Type[BaseCodeGeneratorSettings]):
        """
        Initialize a new registry entry.

        :param generator_cls: The code generator class to register.
        :param settings_cls: The settings class associated with the generator.
        """
        self.generator_cls = generator_cls
        self.settings_cls = settings_cls

    @property
    def name(self) -> str:
        """
        Return the name of the registered generator.

        This is delegated to the `name` attribute of the generator class.

        :return: The human-readable name of the generator.
        """
        return self.generator_cls.name
