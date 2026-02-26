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
from pathlib import Path
import wx
from webweaver.studio.studio_app_settings import StudioAppSettings


class AppSettingsManager:
    """
    Manages persistence of application-level settings using wx.Config.

    This class provides a small abstraction layer over wx.Config to
    load and save StudioAppSettings. It is responsible only for
    translating between the persistent configuration store and the
    strongly-typed StudioAppSettings model.

    Storage Backend:
        Settings are stored using wx.Config under the application
        name "WebWeaverStudio".

    Responsibilities:
        - Read persisted configuration values
        - Provide sensible defaults when values are missing
        - Write updated settings back to persistent storage
        - Flush changes to disk

    This class does not contain business logic — it strictly handles
    persistence concerns.
    """

    def __init__(self):
        """
        Initialise the settings manager and bind to the application's
        wx.Config store.
        """
        self._config = wx.Config("WebWeaverStudio")

    def load(self) -> StudioAppSettings:
        """
        Load application settings from persistent storage.

        Returns:
            StudioAppSettings: A populated settings object. If a value
            is not present in the configuration store, a sensible
            default is used.
        """
        # General Settings
        restore_last_solution = self._config.ReadBool("restore_last_solution",
                                                      False)
        start_maximised = self._config.ReadBool("start_maximised", False)

        # Code Generation settings
        code_generators_path = self._config.Read("code_generators_path", "")

        return StudioAppSettings(
            code_generators_path=Path(code_generators_path) \
                if code_generators_path else Path(),
            restore_last_solution=restore_last_solution,
            start_maximised=start_maximised)

    def save(self, settings: StudioAppSettings):
        """
        Persist application settings to storage.

        Args:
            settings (StudioAppSettings):
                The settings object to persist.

        This method writes values to wx.Config and flushes the
        configuration to ensure changes are committed.
        """
        self._config.Write("code_generators_path",
                           str(settings.code_generators_path))
        self._config.WriteBool("restore_last_solution",
                               settings.restore_last_solution)
        self._config.WriteBool("start_maximised",
                               settings.start_maximised)
        self._config.Flush()
