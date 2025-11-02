"""
Copyright (C) 2025  Web Weaver Development Team
SPDX-License-Identifier: GPL-3.0-or-later

This file is part of Web Weaver (https://github.com/SwatKat1977/WebWeaver).
See the LICENSE file in the project root for full license details.
"""
import wx


class PreferencesDialog(wx.Dialog):
    """Dialog for editing user preferences related to the node editor.

    Provides a simple interface for configuring grid snapping options,
    including enabling/disabling snapping and adjusting the snap grid size.
    """
    # pylint: disable=too-few-public-methods

    def __init__(self, parent, settings):
        """Initialise the preferences dialog.

        Args:
            parent (wx.Window): The parent window or frame that owns this
                                dialog.
            settings (dict): Dictionary of current editor settings, expected
                             to contain:
                - "snap_enabled" (bool): Whether grid snapping is enabled.
                - "snap_size" (int): The grid size in pixels.
        """
        super().__init__(parent, title="Preferences", size=(320, 180))
        vbox = wx.BoxSizer(wx.VERTICAL)

        self.chk_snap = wx.CheckBox(self, label="Enable Grid Snapping")
        self.chk_snap.SetValue(settings["snap_enabled"])

        grid = wx.FlexGridSizer(1, 2, 8, 8)
        grid.Add(wx.StaticText(self, label="Snap Size (px):"), 0, wx.ALIGN_CENTER_VERTICAL)
        self.spin_snap = wx.SpinCtrl(self, min=5, max=200, initial=settings["snap_size"])
        grid.Add(self.spin_snap, 1, wx.EXPAND)

        vbox.Add(self.chk_snap, 0, wx.ALL, 10)
        vbox.Add(grid, 0, wx.ALL | wx.EXPAND, 10)
        vbox.Add(self.CreateSeparatedButtonSizer(wx.OK | wx.CANCEL), 0, wx.EXPAND | wx.ALL, 8)

        self.SetSizer(vbox)
