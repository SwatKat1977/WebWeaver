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
from enum import Enum


class AssertionOperator(str, Enum):
    """
    Enumeration of supported assertion operators.

    Each operator defines the comparison or validation rule applied
    during assertion step execution. The enum inherits from `str`
    so that values can be serialized directly (e.g., into JSON) and
    persisted in step payloads without additional conversion.

    Categories
    ----------
    Binary operators (require left and right values):
        - EQUALS
        - NOT_EQUALS
        - GREATER_THAN
        - LESS_THAN
        - CONTAINS
        - IN
        - STARTS_WITH
        - ENDS_WITH
        - MATCHES_REGEX

    Unary operators (require only a left value):
        - IS_TRUE
        - IS_FALSE
        - IS_NONE
        - IS_NOT_NONE

    Notes
    -----
    Operators listed as unary should also be included in
    `UNARY_OPERATORS` to ensure UI components (such as
    AssertionStepEditor) correctly disable the right-hand input.
    """
    EQUALS = "equals"
    NOT_EQUALS = "not_equals"
    GREATER_THAN = "greater_than"
    LESS_THAN = "less_than"
    CONTAINS = "contains"
    IN = "in"
    STARTS_WITH = "starts_with"
    ENDS_WITH = "ends_with"
    MATCHES_REGEX = "matches_regex"
    IS_TRUE = "is_true"
    IS_FALSE = "is_false"
    IS_NONE = "is_none"
    IS_NOT_NONE = "is_not_none"


"""
Set of assertion operators that do not require a right-hand value.

Operators included here are treated as unary during both UI editing
and playback execution. When selected in the editor, the right-hand
input control is disabled and cleared automatically.

This set must remain consistent with the unary operators defined in
`AssertionOperator` to prevent mismatches between UI behavior and
execution logic.
"""
UNARY_OPERATORS = {
    AssertionOperator.IS_TRUE,
    AssertionOperator.IS_FALSE,
    AssertionOperator.IS_NONE,
    AssertionOperator.IS_NOT_NONE,
}
