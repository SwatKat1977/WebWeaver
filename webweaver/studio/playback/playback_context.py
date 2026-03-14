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
from dataclasses import dataclass
from urllib.parse import urlparse, parse_qs
import re


class PlaybackVariableError(Exception):
    """Raised when a required playback variable is missing."""


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

    _template_pattern = re.compile(r"\{\{([a-zA-Z0-9_\.\-]+)(?:\|([^}]+))?\}\}")

    def __init__(self, driver):
        """
        Initialise an empty playback context.
        """
        self._driver = driver
        self._variables: dict[str, object] = {}

        self._builtins = {
            "CURRENT_URL": self._builtin_current_url,
            "URL_DOMAIN": self._builtin_domain,
            "URL_PROTOCOL": self._builtin_protocol,
            "URL_PATH": self._builtin_path,
            "URL_PARAMETER": self._builtin_url_parameter
        }

    def set_variable(self, name: str, value):
        """
        Store or overwrite a variable in the context.

        Args:
            name: Variable name.
            value: Value to store (any object).
        """
        self._variables[name] = value

    def get_variable(self, name: str):
        """Return a stored variable.

        Args:
            name: Variable name.

        Returns:
            The stored variable value.

        Raises:
            PlaybackVariableError: If the variable does not exist.
        """
        try:
            return self._variables[name]
        except KeyError as ex:
            raise PlaybackVariableError(
                f"Playback variable '{name}' was not found") from ex

    def has_variable(self, name: str) -> bool:
        """
        Check whether a variable exists.

        Args:
            name: Variable name.

        Returns:
            True if the variable exists, otherwise False.
        """
        return name in self._variables

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

        def replace(match):
            name = match.group(1)
            arg = match.group(2)

            # Built-in variable
            if name in self._builtins:
                value = self._builtins[name](arg)
                return str(value)

            # User variable
            value = self.get_variable(name)
            return str(value)

        return self._template_pattern.sub(replace, text)

    def _builtin_current_url(self, arg=None):
        return self._driver.current_url


    def _builtin_domain(self, arg=None):
        return urlparse(self._driver.current_url).hostname or ""


    def _builtin_protocol(self, arg=None):
        return urlparse(self._driver.current_url).scheme


    def _builtin_path(self, arg=None):
        return urlparse(self._driver.current_url).path

    def _builtin_url_parameter(self, arg):
        if not arg:
            return ""

        params = parse_qs(urlparse(self._driver.current_url).query)
        return params.get(arg, [""])[0]
