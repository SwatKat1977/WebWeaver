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
import typing
import wx
from webweaver.studio.ui.framework.page_definition import PageDefinition
from webweaver.studio.ui.framework.settings_page import SettingsPage

class SettingsDialog(wx.Dialog):
    """
    A modal dialog that presents application settings organised
    as a navigable tree of pages.

    The dialog consists of:

        - A wx.TreeCtrl on the left used to navigate between
          available settings pages.
        - A content area on the right where the selected
          SettingsPage instance is displayed.

    Page Lifecycle & Ownership:
        SettingsPage instances are created and owned by this dialog.
        A single instance of each page is constructed during dialog
        initialisation and stored internally. These instances remain
        alive for the lifetime of the dialog and are shown/hidden
        as the user navigates the tree.

        The dialog is responsible for:
            - Creating page instances
            - Managing layout and visibility
            - Destroying pages when the dialog is destroyed
    """
    # pylint: disable=too-few-public-methods

    def __init__(self,
                 parent: wx.Window,
                 context,
                 page_definitions: typing.List[PageDefinition]):
        """
        Initialise the settings dialog.

        Args:
            parent:
                The parent wx window.

            context:
                Application-specific context object passed to
                each SettingsPage during construction.

            page_definitions (List[PageDefinition]):
                Definitions describing the settings pages to
                construct and register in the navigation tree.
        """
        super().__init__(parent)

        self._context = context
        self._page_definitions: typing.List[PageDefinition] = page_definitions

        self._tree = wx.TreeCtrl(self)
        self._content_area = wx.Panel(self)

        # Maps tree items to their corresponding SettingsPage instance.
        # Each page instance is created once and reused while the dialog
        # remains open.
        self._pages: dict[wx.TreeItemId, SettingsPage] = {}
