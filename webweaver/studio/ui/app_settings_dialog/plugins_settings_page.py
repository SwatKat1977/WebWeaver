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

        outer = wx.BoxSizer(wx.VERTICAL)

        # ---- Content container with consistent margins ----
        content  = wx.BoxSizer(wx.VERTICAL)

        # ===== Section Title =====
        title = wx.StaticText(self, label="Code Generator Plugins")
        font = title.GetFont()
        font = font.Bold()
        font.SetPointSize(font.GetPointSize() + 1)
        title.SetFont(font)
        content.Add(title, 0, wx.BOTTOM, 10)

        # ===== Divider line =====
        content.Add(wx.StaticLine(self), 0, wx.EXPAND | wx.BOTTOM, 20)

        # --- Code Generation Plugin field Area ---
        label = wx.StaticText(self,
                               label="Code Generator Plugins Path")
        font = label.GetFont()
        font = font.Bold()
        label.SetFont(font)
        content.Add(label, 0, wx.BOTTOM, 6)

        self._code_gen_dir_picker = wx.DirPickerCtrl(
            self, message="Select code generator directory")
        content.Add(self._code_gen_dir_picker, 0, wx.EXPAND)

        # Add content with clean outer padding
        outer.Add(content, 0, wx.ALL | wx.EXPAND, 20)

        # Push everything upward
        outer.AddStretchSpacer()

        self.SetSizer(outer)

    def load(self):
        """
        Populate the directory picker with the current plugins path
        from the settings model.
        """
        self._code_gen_dir_picker.SetPath(
            str(self._settings.code_generators_path))

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
        self._settings.code_generators_path = \
            Path(self._code_gen_dir_picker.GetPath())
