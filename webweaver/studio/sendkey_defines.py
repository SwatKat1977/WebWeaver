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
from enum import Enum


class SendkeyModify(Enum):
    """
    Modifier keys that can be combined with other keys when sending keyboard
    input.

    These represent standard keyboard modifier keys that alter the behavior
    of another key press (for example: CTRL+C, ALT+TAB, SHIFT+A).
    """
    CTRL = "ctrl"
    ALT = "alt"
    SHIFT = "shift"


class SendkeySpecialKey(Enum):
    """
    Special non-character keys that can be sent as part of keyboard automation.

    These represent keys that do not correspond to printable characters but
    instead perform control or navigation actions such as ENTER, TAB, or
    arrow keys.
    """
    ENTER = "enter"
    TAB = "tab"
    ESCAPE = "escape"
    BACKSPACE = "backspace"
    DELETE = "delete"
    SPACE = "space"
    ARROW_UP = "arrow_up"
    ARROW_DOWN = "arrow_down"
    ARROW_LEFT = "arrow_left"
    ARROW_RIGHT = "arrow_right"
    HOME = "home"
    END = "end"
    PAGE_UP = "page_up"
    PAGE_DOWN = "page_down"
