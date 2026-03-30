"""
This source file is part of Web Weaver
For the latest info, see https://github.com/SwatKat1977/WebWeaver

Copyright 2025-2026 SwatKat1977

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.
"""
import enum
import typing
from dataclasses import dataclass


class ConfigItemDataType(enum.Enum):
    """ Enumeration for configuration item data type """
    INTEGER = enum.auto()
    STRING = enum.auto()


@dataclass(frozen=True)
class ConfigurationSetupItem:
    """ Configuration layout class """

    item_name : str
    valid_values : typing.Optional[list]
    is_required : bool
    item_type : ConfigItemDataType
    default_value : typing.Optional[object]

    def __init__(self, item_name: str, item_type : ConfigItemDataType,
                 valid_values: typing.Optional[list] = None,
                 is_required: bool = False,
                 default_value: typing.Optional[object] = None) -> None:
        # pylint: disable=too-many-arguments, too-many-positional-arguments
        object.__setattr__(self, "item_name", item_name)
        object.__setattr__(self, "item_type", item_type)
        object.__setattr__(self, "valid_values",
                           valid_values if valid_values else [])
        object.__setattr__(self, "is_required", is_required)
        object.__setattr__(self, "default_value",
                           default_value if default_value else [])


class ConfigurationSetup:
    """ Class that defines the configuration Format """

    def __init__(self, setup_items : dict) -> None:
        self._items = setup_items

    def get_sections(self) -> list:
        """
        Get a list of sections available.

        returns:
            List of strings that represent the sections available.
        """
        return list(self._items.keys())

    def get_section(self, name: str):
        """
        Get a list of items within a given sections.

        returns:
            List of list of configuration items.
        """
        if name not in self._items:
            return None

        return self._items[name]
