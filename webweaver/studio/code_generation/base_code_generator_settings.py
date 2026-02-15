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
from abc import ABC, abstractmethod


class BaseCodeGeneratorSettings(ABC):
    """
    Base class for generator-specific settings.

    This abstract class defines the interface that all code generator
    settings implementations must follow. Concrete subclasses are expected
    to provide serialization and deserialization logic so that settings
    can be easily persisted and restored.

    Implementations should ensure that all relevant configuration values
    are properly handled by the `to_json` and `from_json` methods.
    """

    @abstractmethod
    def to_json(self) -> dict:
        """
        Serialize the current settings instance to a JSON-compatible dictionary.

        Returns:
            dict: A dictionary representation of the settings suitable for
            JSON serialization.
        """

    @abstractmethod
    def from_json(self, data: dict) -> None:
        """
        Load settings values from a JSON-compatible dictionary.

        This method should update the current instance using the values
        provided in the given dictionary.

        Args:
            data (dict): A dictionary containing serialized settings data.

        Raises:
            ValueError: If the provided data is invalid or missing required fields.
        """
