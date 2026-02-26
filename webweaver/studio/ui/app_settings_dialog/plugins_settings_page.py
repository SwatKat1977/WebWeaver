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
from webweaver.studio.ui.framework.settings_page import SettingsPage
from webweaver.studio.studio_app_settings import StudioAppSettings


class PluginsSettingsPage(SettingsPage):
    """
    Settings page responsible for configuring the application's
    plugins directory.

    This page allows the user to select a filesystem directory
    where plugins are discovered and loaded from.

    The page operates directly on a StudioAppSettings instance
    provided at construction time. Changes are written back to
    that instance when `apply()` is called.
    """

    def __init__(self, parent, context: StudioAppSettings):
        """
        Initialise the plugins settings page.

        Args:
            parent:
                The parent wx window.

            context (StudioAppSettings):
                The application settings model instance that this
                page reads from and writes to.
        """
        super().__init__(parent)
        self._settings = context

        main_sizer  = wx.BoxSizer(wx.VERTICAL)

        # Add top spacer
        main_sizer.AddSpacer(20)

        content_sizer = wx.BoxSizer(wx.VERTICAL)

        label = wx.StaticText(
            self,
            label="Code Generator Plugins Path"
        )
        font = label.GetFont()
        font = font.Bold()
        label.SetFont(font)
        content_sizer.Add(label, 0, wx.BOTTOM, 6)

        self._dir_picker = wx.DirPickerCtrl(
            self, message="Select plugins directory")
        content_sizer.Add(self._dir_picker, 0, wx.EXPAND)

        main_sizer.Add(content_sizer, 0, wx.ALL | wx.EXPAND, 2)

        self.SetSizer(main_sizer)

    def load(self):
        """
        Populate the directory picker with the current plugins path
        from the settings model.
        """
        self._dir_picker.SetPath(str(self._settings.plugins_path))

    def validate(self) -> bool:
        """
        Validate the selected plugins directory.

        Returns:
            bool: True if the selected path is acceptable.

        Note:
            Currently no validation is performed. Future implementations
            may check that the directory exists or meets specific criteria.
        """

        # could check path exists if you want
        return True

    def apply(self):
        """
        Persist the selected directory back to the settings model.

        The chosen path is written to the associated
        StudioAppSettings instance.
        """
        self._settings.plugins_path = Path(self._dir_picker.GetPath())
