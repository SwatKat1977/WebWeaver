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
import re


class PlaybackContext:
    """
    Stores and resolves runtime variables used during playback.

    This context acts as a lightweight key/value store that allows
    playback steps to share state and perform template substitution
    using {{variable}} placeholders.

    Example:
        context.set_variable("username", "alice")
        context.resolve_template("Hello {{username}}")
        # -> "Hello alice"
    """

    _template_pattern = re.compile(r"\{\{([a-zA-Z0-9_\.\-]+)\}\}")

    def __init__(self):
        """
        Initialise an empty playback context.
        """
        self._variables: dict[str, object] = {}

    def set_variable(self, name: str, value):
        """
        Store or overwrite a variable in the context.

        Args:
            name: Variable name.
            value: Value to store (any object).
        """
        self._variables[name] = value

    def get_variable(self, name: str, default=None):
        """
        Retrieve a variable value.

        Args:
            name: Variable name.
            default: Value returned if the variable does not exist.

        Returns:
            The stored variable value, or `default` if missing.
        """
        return self._variables.get(name, default)

    def has_variable(self, name: str) -> bool:
        """
        Check whether a variable exists.

        Args:
            name: Variable name.

        Returns:
            True if the variable exists, otherwise False.
        """
        return name in self._variables

    def require_variable(self, name: str):
        """
        Retrieve a variable, raising if it does not exist.

        Args:
            name: Variable name.

        Returns:
            The stored variable value.

        Raises:
            KeyError: If the variable is not present.
        """
        if name not in self._variables:
            raise KeyError(f"Playback variable '{name}' not found")
        return self._variables[name]

    def variables(self) -> dict[str, object]:
        """
        Return a shallow copy of all stored variables.

        Returns:
            A new dictionary containing all variables.
        """
        return dict(self._variables)

    def clear(self):
        """
        Remove all variables from the context.
        """
        self._variables.clear()

    def resolve_template(self, text: str) -> str:
        """
        Replace {{variable}} placeholders in text using stored variables.

        Variable names may include letters, digits, underscores,
        dots, and hyphens.

        Missing variables resolve to an empty string.

        Args:
            text: Input text containing optional template placeholders.

        Returns:
            The resolved string with placeholders replaced.
        """

        def replace(match):
            name = match.group(1)
            value = self.get_variable(name, "")
            return str(value)

        return self._template_pattern.sub(replace, text)
