"""
Copyright (C) 2025  Web Weaver Development Team
SPDX-License-Identifier: GPL-3.0-or-later

This file is part of Web Weaver (https://github.com/SwatKat1977/WebWeaver).
See the LICENSE file in the project root for full license details.
"""
from dataclasses import dataclass
from enum import Enum
import typing


class PinType(Enum):
    EXECUTE = "exec"
    BOOLEAN = "bool"
    INTEGER = "int"
    FLOAT = "float"
    STRING = "string"
    CUSTOM = "custom"


DEFAULT_PIN_COLOUR: typing.Tuple = (200, 200, 200)


@dataclass
class NodePin:
    name: str
    pin_type: PinType = PinType.EXECUTE
    colour: typing.Tuple[int, int, int] = DEFAULT_PIN_COLOUR
