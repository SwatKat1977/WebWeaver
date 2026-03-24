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
from webweaver.studio.recording.recording_event_type import RecordingEventType


TOOLBOX_ACTION_MAP = {

    # DOM Actions
    "Check": RecordingEventType.DOM_CHECK,
    "Click": RecordingEventType.DOM_CLICK,
    "Get DOM Value": RecordingEventType.DOM_GET,
    "Select": RecordingEventType.DOM_SELECT,
    "Type": RecordingEventType.DOM_TYPE,

    # Browser
    "Navigate": RecordingEventType.NAV_GOTO,
    # self.tree.AppendItem(browser, "Refresh")
    "Scroll": RecordingEventType.SCROLL,
    "Wait": RecordingEventType.WAIT,

    # Logic
    "Rest API": RecordingEventType.REST_API,
    "Send Keys": RecordingEventType.SENDKEYS,
    "User Variable": RecordingEventType.USER_VARIABLE,
    # "Loop": RecordingEventType.LOOP,

    # General
    # "Group": RecordingEventType.REST_API,
}


class ToolboxPanel(wx.Panel):
    """
    Toolbox panel containing available actions that can be inserted
    into a recording.
    """

    def __init__(self, parent):
        """
        Initialize the toolbox panel.

        Args:
            parent (wx.Window): Parent window that owns this panel.
        """
        super().__init__(parent)

        self._placeholder: typing.Optional[wx.StaticText] = None
        self._toolbox_tree: typing.Optional[wx.TreeCtrl] = None

        self._create_ui()
        self.show_no_recording()

    def show_no_recording(self):
        """
        Display the placeholder message indicating that no recording
        is currently open and hide the toolbox tree.
        """
        self._toolbox_tree.Hide()
        self._placeholder.Show()
        self.Layout()

    def show_toolbox_items(self) -> None:
        """
        Display the toolbox tree containing available actions and
        hide the placeholder message.
        """
        self._placeholder.Hide()
        self._toolbox_tree.Show()
        self._toolbox_tree.ExpandAll()
        self.Layout()

    def _create_ui(self):
        """
        Create and initialize the user interface elements for the
        toolbox panel.

        This includes:

        - A placeholder label shown when no recording is open.
        - A tree control listing all available toolbox actions.
        - Event bindings for user interaction.
        """
        sizer = wx.BoxSizer(wx.VERTICAL)

        # -- Placeholder text --
        self._placeholder = wx.StaticText(self,
                                          label="No recording open")
        self._placeholder.SetForegroundColour(wx.Colour(120, 120, 120))

        # -- Actual tree --
        self._toolbox_tree = wx.TreeCtrl(
            self,
            style=wx.TR_DEFAULT_STYLE
                  | wx.TR_HIDE_ROOT
                  | wx.TR_LINES_AT_ROOT)

        # Populate toolbox tree with available actions.
        root = self._toolbox_tree.AddRoot("Toolbox")

        dom = self._toolbox_tree.AppendItem(root, "DOM Actions")
        self._toolbox_tree.AppendItem(dom, "Check")
        self._toolbox_tree.AppendItem(dom, "Click")
        self._toolbox_tree.AppendItem(dom, "Get DOM Value")
        self._toolbox_tree.AppendItem(dom, "Select")
        self._toolbox_tree.AppendItem(dom, "Type")

        browser = self._toolbox_tree.AppendItem(root, "Browser")
        self._toolbox_tree.AppendItem(browser, "Navigate")
        self._toolbox_tree.AppendItem(browser, "Scroll")
        self._toolbox_tree.AppendItem(browser, "Wait")
        # self.tree.AppendItem(browser, "Refresh")

        logic = self._toolbox_tree.AppendItem(root, "Logic")
        self._toolbox_tree.AppendItem(logic, "Rest API")
        self._toolbox_tree.AppendItem(logic, "Send Keys")
        self._toolbox_tree.AppendItem(logic, "User Variable")
        # self.tree.AppendItem(logic, "Loop")

        assertion = self._toolbox_tree.AppendItem(root, "Validation")
        self._toolbox_tree.AppendItem(assertion, "Assert")
        # self.tree.AppendItem(logic, "Loop")

        # general = self._toolbox_tree.AppendItem(root, "General")
        # self._toolbox_tree.AppendItem(general, "Group")

        self._toolbox_tree.ExpandAll()

        self._toolbox_tree.Bind(wx.EVT_TREE_ITEM_ACTIVATED,
                                self._on_item_activated)

        sizer.Add(self._placeholder, 1, wx.ALIGN_CENTER | wx.ALL, 10)
        sizer.Add(self._toolbox_tree, 1, wx.EXPAND | wx.ALL, 5)

        self.SetSizer(sizer)

        self._toolbox_tree.Bind(wx.EVT_TREE_BEGIN_DRAG, self._on_begin_drag)

    def _on_item_activated(self, event):
        """
        Handle activation of a toolbox item.

        This event is triggered when the user double-clicks an item in
        the toolbox tree. The selected action name is retrieved and can
        later be used to insert a corresponding step into the current
        recording.

        Args:
            event (wx.TreeEvent): Tree activation event.
        """
        item = event.GetItem()

        if not item.IsOk():
            return

        action_name = self._toolbox_tree.GetItemText(item)

        print(f"Toolbox action selected: {action_name}")
        # Later this should insert a step into the recording.

    def _on_begin_drag(self, event):
        """Starts a drag operation from the toolbox tree."""

        item = event.GetItem()

        if not item.IsOk():
            return

        # Prevent dragging category/group nodes
        if self._toolbox_tree.ItemHasChildren(item):
            return

        label = self._toolbox_tree.GetItemText(item)

        if not label:
            return

        event_type = TOOLBOX_ACTION_MAP.get(label)

        if not event_type:
            return

        data = wx.TextDataObject(event_type.value)

        source = wx.DropSource(self._toolbox_tree)
        source.SetData(data)

        source.DoDragDrop(wx.Drag_CopyOnly)
