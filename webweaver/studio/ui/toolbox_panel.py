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
import wx


class ToolboxPanel(wx.Panel):
    """
    Toolbox panel containing available actions that can be inserted
    into a recording.
    """

    def __init__(self, parent):
        super().__init__(parent)

        sizer = wx.BoxSizer(wx.VERTICAL)

        self.tree = wx.TreeCtrl(
            self,
            style=wx.TR_DEFAULT_STYLE
                  | wx.TR_HIDE_ROOT
                  | wx.TR_LINES_AT_ROOT
        )

        sizer.Add(self.tree, 1, wx.EXPAND | wx.ALL, 5)

        self.SetSizer(sizer)

        self._build_tree()

        self.tree.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self._on_item_activated)

    # ------------------------------------------------------------------

    def _build_tree(self):
        """
        Populate toolbox tree with available actions.
        """

        root = self.tree.AddRoot("Toolbox")

        dom = self.tree.AppendItem(root, "DOM Actions")
        self.tree.AppendItem(dom, "Check")
        self.tree.AppendItem(dom, "Click")
        self.tree.AppendItem(dom, "Get DOM Value")
        self.tree.AppendItem(dom, "Type")
        self.tree.AppendItem(dom, "Select")
        self.tree.AppendItem(dom, "Wait")

        browser = self.tree.AppendItem(root, "Browser")
        self.tree.AppendItem(browser, "Navigate")
        self.tree.AppendItem(browser, "Scroll")
        # self.tree.AppendItem(browser, "Refresh")

        logic = self.tree.AppendItem(root, "Logic")
        self.tree.AppendItem(logic, "Group")
        self.tree.AppendItem(logic, "Rest API")
        # self.tree.AppendItem(logic, "Loop")

        assertion = self.tree.AppendItem(root, "Assertion")
        self.tree.AppendItem(assertion, "Assert")
        # self.tree.AppendItem(logic, "Loop")

        self.tree.ExpandAll()

    # ------------------------------------------------------------------

    def _on_item_activated(self, event):
        """
        Called when user double-clicks an action.
        """
        item = event.GetItem()

        if not item.IsOk():
            return

        action_name = self.tree.GetItemText(item)

        print(f"Toolbox action selected: {action_name}")
        # Later this should insert a step into the recording.
