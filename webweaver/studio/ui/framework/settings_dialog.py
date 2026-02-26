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

        # Maps tree items to their corresponding SettingsPage instance.
        # Each page instance is created once and reused while the dialog
        # remains open.
        self._pages: dict[wx.TreeItemId, SettingsPage] = {}

        self._create_ui()

    def _create_ui(self):
        self._tree = wx.TreeCtrl(self)
        self._tree.SetMinSize((200, -1))

        self._content_area = wx.Panel(self)

        self._content_sizer = wx.BoxSizer(wx.VERTICAL)
        self._content_area.SetSizer(self._content_sizer)

        main_sizer = wx.BoxSizer(wx.VERTICAL)

        body_sizer = wx.BoxSizer(wx.HORIZONTAL)
        body_sizer.Add(self._tree, 0, wx.EXPAND | wx.ALL, 5)
        body_sizer.Add(self._content_area, 1, wx.EXPAND | wx.ALL, 5)

        button_sizer = self.CreateSeparatedButtonSizer(
            wx.OK | wx.CANCEL | wx.APPLY)

        main_sizer.Add(body_sizer, 1, wx.EXPAND)
        main_sizer.Add(button_sizer, 0, wx.EXPAND | wx.ALL, 5)

        self.SetSizer(main_sizer)
        self.SetSize((700, 500))

        root = self._tree.AddRoot("Settings")

        for definition in self._page_definitions:
            item = self._tree.AppendItem(root, definition.label)

            page = definition.page_class(self._content_area, self._context)
            page.Hide()
            page.load()

            self._content_sizer.Add(page, 1, wx.EXPAND)

            self._pages[item] = page

        # Expand Root
        self._tree.Expand(root)

        # Select first item automatically
        first_item, _ = self._tree.GetFirstChild(root)
        if first_item.IsOk():
            self._tree.SelectItem(first_item)
            self._show_page(first_item)

        self._tree.Bind(wx.EVT_TREE_SEL_CHANGED,
                        self._on_tree_selection_changed)

        self.Bind(wx.EVT_BUTTON, self._on_ok, id=wx.ID_OK)
        self.Bind(wx.EVT_BUTTON, self._on_apply, id=wx.ID_APPLY)

    def _show_page(self, item: wx.TreeItemId):
        for page in self._pages.values():
            page.Hide()

        selected_page = self._pages.get(item)
        if selected_page:
            selected_page.Show()
            self._content_area.Layout()

    def _on_tree_selection_changed(self, event):
        item = event.GetItem()
        self._show_page(item)

    def _apply_all(self) -> bool:
        for page in self._pages.values():
            if not page.validate():
                return False

        for page in self._pages.values():
            page.apply()

        return True

    def _on_ok(self, _event):
        if self._apply_all():
            self.EndModal(wx.ID_OK)

    def _on_apply(self, _event):
        self._apply_all()
