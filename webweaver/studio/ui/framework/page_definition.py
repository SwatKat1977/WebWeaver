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
import dataclasses
import typing
from webweaver.studio.ui.framework.settings_page import SettingsPage


@dataclasses.dataclass
class PageDefinition:
    """
    Describes a settings page that can be registered and displayed
    within the application.

    A PageDefinition acts as lightweight metadata used to construct
    and organise settings pages in the UI.

    Attributes:
        label (str):
            Human-readable name of the page as shown in the UI.

        page_class (Type[SettingsPage]):
            The concrete SettingsPage subclass that should be
            instantiated when this page is opened.

        icon (Optional[str]):
            Optional identifier or path for an icon associated
            with the page. Reserved for future use.

        path (Optional[list[str]]):
            Optional hierarchical path used to group or nest the
            page within a settings tree structure.
            For example: ["General", "Appearance"].
            Reserved for future use.
    """
    label: str
    page_class: typing.Type[SettingsPage]
    icon: typing.Optional[str] = None               # Future
    path: typing.Optional[list[str]] = None         # Future
