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
import typing
import wx


class ToolboxPanel(wx.Panel):
    """
    Toolbox panel containing available actions that can be inserted
    into a recording.
    """

    def __init__(self, parent):
        super().__init__(parent)

        sizer = wx.BoxSizer(wx.VERTICAL)

        self._placeholder: typing.Optional[wx.StaticText] = None
        self._tree: typing.Optional[wx.TreeCtrl] = None

        self._create_ui()
        self.show_no_recording()

    def show_no_recording(self):
        self._tree.Hide()
        self._placeholder.Show()
        self.Layout()

    def show_toolbox_items(self) -> None:
        self._placeholder.Hide()
        self._tree.Show()
        self._tree.ExpandAll()
        self.Layout()

    def _create_ui(self):
        sizer = wx.BoxSizer(wx.VERTICAL)

        # -- Placeholder text --
        self._placeholder = wx.StaticText(self,
                                          label="No recording open")
        self._placeholder.SetForegroundColour(wx.Colour(120, 120, 120))

        # -- Actual tree --
        self._tree = wx.TreeCtrl(
            self,
            style=wx.TR_DEFAULT_STYLE
                  | wx.TR_HIDE_ROOT
                  | wx.TR_LINES_AT_ROOT)

        """
        Populate toolbox tree with available actions.
        """

        root = self._tree.AddRoot("Toolbox")

        dom = self._tree.AppendItem(root, "DOM Actions")
        self._tree.AppendItem(dom, "Check")
        self._tree.AppendItem(dom, "Click")
        self._tree.AppendItem(dom, "Get DOM Value")
        self._tree.AppendItem(dom, "Type")
        self._tree.AppendItem(dom, "Select")
        self._tree.AppendItem(dom, "Wait")

        browser = self._tree.AppendItem(root, "Browser")
        self._tree.AppendItem(browser, "Navigate")
        self._tree.AppendItem(browser, "Scroll")
        # self.tree.AppendItem(browser, "Refresh")

        logic = self._tree.AppendItem(root, "Logic")
        self._tree.AppendItem(logic, "Group")
        self._tree.AppendItem(logic, "Rest API")
        # self.tree.AppendItem(logic, "Loop")

        assertion = self._tree.AppendItem(root, "Assertion")
        self._tree.AppendItem(assertion, "Assert")
        # self.tree.AppendItem(logic, "Loop")

        self._tree.ExpandAll()

        self._tree.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self._on_item_activated)

        sizer.Add(self._placeholder, 1, wx.ALIGN_CENTER | wx.ALL, 10)
        sizer.Add(self._tree, 1, wx.EXPAND | wx.ALL, 5)

        self.SetSizer(sizer)

    def _on_item_activated(self, event):
        """
        Called when user double-clicks an action.
        """
        item = event.GetItem()

        if not item.IsOk():
            return

        action_name = self._tree.GetItemText(item)

        print(f"Toolbox action selected: {action_name}")
        # Later this should insert a step into the recording.
