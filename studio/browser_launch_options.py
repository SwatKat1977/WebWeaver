"""
This source file is part of Web Weaver
For the latest info, see https://github.com/SwatKat1977/WebWeaver

Copyright 2025 SwatKat1977

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
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Dict, Any


@dataclass
class WindowSize:
    """
    Represents a window size in pixels.

    This is a simple value object used to describe the width and height
    of a browser window when launching a session.
    """

    width: int = 0
    """The width of the window in pixels."""

    height: int = 0
    """The height of the window in pixels."""

    def to_dict(self) -> Dict[str, int]:
        """
        Convert the window size to a JSON-serialisable dictionary.

        Returns
        -------
        Dict[str, int]
            A dictionary containing 'width' and 'height' entries.
        """
        return {
            "width": self.width,
            "height": self.height,
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> Optional["WindowSize"]:
        """
        Create a WindowSize instance from a dictionary.

        The dictionary is expected to contain integer 'width' and
        'height' values. If the input is invalid or incomplete,
        None is returned.

        Parameters
        ----------
        data : Dict[str, Any]
            Dictionary containing window size data.

        Returns
        -------
        Optional[WindowSize]
            A WindowSize instance if parsing succeeds, otherwise None.
        """
        if not isinstance(data, dict):
            return None

        width = data.get("width")
        height = data.get("height")

        if isinstance(width, int) and isinstance(height, int):
            return WindowSize(width=width, height=height)

        return None


@dataclass
class BrowserLaunchOptions:
    """
    Describes configuration options used when launching a browser.

    This class encapsulates browser startup preferences such as privacy
    mode, extension handling, window size, and user agent overrides.
    It supports round-trip serialisation to and from dictionaries.
    """

    private_mode: bool = True
    """Whether the browser should be launched in private/incognito mode."""

    disable_extensions: bool = True
    """Whether browser extensions should be disabled."""

    disable_notifications: bool = True
    """Whether browser notifications should be suppressed."""

    ignore_certificate_errors: bool = False
    """Whether SSL/TLS certificate errors should be ignored."""

    user_agent: Optional[str] = None
    """Optional user agent string override."""

    window_size: Optional[WindowSize] = None
    """Optional explicit window size to use when launching the browser."""

    maximised: bool = False
    """Whether the browser window should start maximised."""

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the launch options to a JSON-serialisable dictionary.

        Only optional fields that are explicitly set are included in
        the output.

        Returns
        -------
        Dict[str, Any]
            A dictionary representation of the launch options.
        """
        data: Dict[str, Any] = {
            "privateMode": self.private_mode,
            "disableExtensions": self.disable_extensions,
            "disableNotifications": self.disable_notifications,
            "ignoreCertificateErrors": self.ignore_certificate_errors,
            "maximised": self.maximised,
        }

        if self.user_agent is not None:
            data["userAgent"] = self.user_agent

        if self.window_size is not None:
            data["windowSize"] = self.window_size.to_dict()

        return data

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "BrowserLaunchOptions":
        """
        Create a BrowserLaunchOptions instance from a dictionary.

        Missing or invalid fields are ignored and default values are
        preserved, matching the behaviour of the original C++
        implementation.

        Parameters
        ----------
        data : Dict[str, Any]
            Dictionary containing browser launch options.

        Returns
        -------
        BrowserLaunchOptions
            A populated BrowserLaunchOptions instance.
        """
        opts = BrowserLaunchOptions()

        if not isinstance(data, dict):
            # No launcher options → defaults
            return opts

        opts.private_mode = data.get("privateMode", opts.private_mode)
        opts.disable_extensions = data.get(
            "disableExtensions", opts.disable_extensions
        )
        opts.disable_notifications = data.get(
            "disableNotifications", opts.disable_notifications
        )
        opts.ignore_certificate_errors = data.get(
            "ignoreCertificateErrors", opts.ignore_certificate_errors
        )
        opts.maximised = data.get("maximised", opts.maximised)

        user_agent = data.get("userAgent")
        if isinstance(user_agent, str):
            opts.user_agent = user_agent

        window_size = data.get("windowSize")
        parsed_ws = WindowSize.from_dict(window_size)
        if parsed_ws is not None:
            opts.window_size = parsed_ws

        return opts
