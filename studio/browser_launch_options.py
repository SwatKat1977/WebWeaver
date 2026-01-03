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
    width: int = 0
    height: int = 0

    def to_dict(self) -> Dict[str, int]:
        return {
            "width": self.width,
            "height": self.height,
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> Optional["WindowSize"]:
        if not isinstance(data, dict):
            return None

        width = data.get("width")
        height = data.get("height")

        if isinstance(width, int) and isinstance(height, int):
            return WindowSize(width=width, height=height)

        return None


@dataclass
class BrowserLaunchOptions:
    private_mode: bool = True
    disable_extensions: bool = True
    disable_notifications: bool = True
    ignore_certificate_errors: bool = False

    user_agent: Optional[str] = None
    window_size: Optional[WindowSize] = None
    maximised: bool = False

    def to_dict(self) -> Dict[str, Any]:
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
