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
from dataclasses import dataclass
from typing import Optional
import wx


@dataclass(frozen=True)
class ValidationResult:
    """
    Represents the outcome of validating a settings page.

    This immutable result object allows a page to communicate not only
    whether validation succeeded, but also provide contextual information
    such as an error message and which control should receive focus.

    Attributes:
        ok (bool):
            True if validation succeeded and the dialog may proceed.
            False if validation failed.

        message (str):
            Optional human-readable validation error message.
            Intended to be displayed to the user when `ok` is False.

        focus (Optional[wx.Window]):
            Optional control that should receive input focus if
            validation fails. Allows the dialog to guide the user
            directly to the problematic field.
    """
    ok: bool
    message: str = ""
    focus: Optional[wx.Window] = None  # control to focus


class SettingsPage(wx.Panel):
    """
    Base class for all settings pages displayed inside a SettingsDialog.

    A SettingsPage encapsulates a specific group of related settings,
    including UI controls and the logic required to:

        - Load current values into the UI
        - Validate user input
        - Apply changes back to the application state

    Lifecycle:

        1. The page is constructed by SettingsDialog.
        2. `load()` is called to populate UI controls with current values.
        3. When the user confirms the dialog:
            - `validate()` is called. If it returns False, the dialog
              should prevent closing.
            - If validation succeeds, `apply()` is called to persist changes.

    Subclasses are expected to override `load()` and `apply()`,
    and optionally `validate()` if validation logic is required.
    """

    def load(self):
        """
        Populate the UI controls with the current settings values.

        This method should read from the application's configuration
        or context and update the page's controls accordingly.
        """

    def validate(self) -> ValidationResult:
        """
        Validate the current user input.

        Returns:
            ValidationResult:
                An object describing whether validation succeeded.
                The default implementation always returns success.

        Subclasses should override this method if custom validation
        logic is required.
        """
        return ValidationResult(ok=True)

    def apply(self):
        """
        Persist the current UI values back to the application state.

        This method should write updated values to the configuration,
        context, or other persistent storage as appropriate.
        """
