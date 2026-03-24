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
from dataclasses import asdict
from enum import Enum
import wx
from webweaver.studio.persistence.recording_persistence import RecordingPersistence
from webweaver.studio.recording.recording_event_type import RecordingEventType
from webweaver.studio.ui.add_step_dialog import default_payload_for
from webweaver.studio.ui.step_information_overlay import StepInformationOverlay


class StepStatus(Enum):
    """Enumeration representing the execution status of a recording step.

    Attributes:
        NOT_RUN: Step has not been executed yet.
        RUNNING: Step is currently executing.
        PASSED: Step completed successfully.
        FAILED: Step execution failed.
        WARNING: Step completed with warnings.
    """
    NOT_RUN = 0
    RUNNING = 1
    PASSED = 2
    FAILED = 3
    WARNING = 4


class ToolboxStepDropTarget(wx.TextDropTarget):
    """Drop target for adding toolbox steps into the recording tree."""
    # pylint: disable=too-few-public-methods

    def __init__(self, tree):
        """Initializes the drop target.

        Args:
            tree (RecordingStepTree): Target tree control.
        """
        super().__init__()
        self.tree = tree

    def OnDropText(self, x, y, text):
        """Handles text dropped from the toolbox.

        Args:
            x (int): Drop x position in tree client coordinates.
            y (int): Drop y position in tree client coordinates.
            text (str): Dropped toolbox text.

        Returns:
            bool: True if the drop was handled successfully, otherwise False.
        """
        # pylint: disable=invalid-name
        return self.tree.handle_toolbox_drop(x, y, text)


class RecordingStepTree(wx.TreeCtrl):
    """Tree control for displaying and managing recording steps.

    Supports hierarchical step grouping, drag-and-drop reordering,
    status icon updates, and hover-based information overlays.
    """
    # pylint: disable=too-many-instance-attributes

    def __init__(self, parent, controller=None):
        """Initializes the step tree control.

        Args:
            parent: Parent wx widget.
        """
        super().__init__(
            parent,
            style=wx.TR_DEFAULT_STYLE |
                  wx.TR_HAS_BUTTONS |
                  wx.TR_LINES_AT_ROOT |
                  wx.TR_FULL_ROW_HIGHLIGHT)

        self.drag_item = None
        self._info_overlay = StepInformationOverlay(self)
        self.hover_item = None
        self.hover_timer = wx.Timer(self)
        self.pending_hover_item = None
        self.drop_indicator_y = None
        self._controller = controller

        self._create_images()

        self.root = self.AddRoot("Steps")
        self.Expand(self.root)

        self.Bind(wx.EVT_TREE_BEGIN_DRAG, self._on_begin_drag)
        self.Bind(wx.EVT_TREE_END_DRAG, self._on_end_drag)
        self.Bind(wx.EVT_MOTION, self._on_mouse_move)
        self.Bind(wx.EVT_LEAVE_WINDOW, self._on_mouse_leave)
        self.Bind(wx.EVT_TIMER, self._on_hover_timer, self.hover_timer)
        self.Bind(wx.EVT_PAINT, self._on_paint)

        self.Bind(wx.EVT_TREE_ITEM_COLLAPSED, self._on_item_collapsed)

        self.SetDropTarget(ToolboxStepDropTarget(self))

        self.ExpandAll()

    @property
    def tree_root(self) -> wx.TreeItemId:
        """Returns the root tree item.

        Returns:
            wx.TreeItemId: Root node of the tree.
        """
        return self.root

    def add_step(self,
                 label: str, data: dict,
                 parent: wx.TreeItemId = None) -> None:
        """Adds a step node to the tree.

        Args:
            label: Display label for the step.
            data: Associated step metadata.
            parent: Optional parent node. Defaults to root.
        """
        parent_node = self.root if parent is None else parent
        self._add_step_entry(parent_node, label, self._icon_not_run, data)
        self.Expand(self.root)

    def add_group(self,
                  parent: wx.TreeItemId,
                  label: str) -> wx.TreeItemId:
        """Adds a group node (non-step container).

        Args:
            parent: Parent tree item.
            label: Group label.

        Returns:
            wx.TreeItemId: Created group node.
        """
        group_item_id = self.AppendItem(parent, label)
        self.SetItemBold(group_item_id)
        return group_item_id

    def handle_toolbox_drop(self, x: int, y: int, text: str) -> bool:
        """Handles a toolbox step being dropped onto the tree.

        Args:
            x (int): Drop x position in client coordinates.
            y (int): Drop y position in client coordinates.
            text (str): Toolbox item text representing the step type.

        Returns:
            bool: True if the step was inserted, otherwise False.
        """
        target, _ = self.HitTest(wx.Point(x, y))

        if not target.IsOk():
            target = self.root

        # Convert incoming text (e.g. "wait") to enum
        event_enum = RecordingEventType(text)

        # Create default payload
        payload = default_payload_for(event_enum)

        item_data = {
            "text": text,
            "icon": self._icon_not_run,
            "data": {
                "type": event_enum.value,
                "payload": asdict(payload)
            },
            "bold": False,
            "expanded": False,
            "children": []
        }

        new_item = self._reinsert_item(target,
                                       item_data,
                                       drop_point=wx.Point(x, y))

        parent = self.GetItemParent(new_item)
        if parent.IsOk():
            self.Expand(parent)

        self.SelectItem(new_item)
        self.EnsureVisible(new_item)

        new_order = self._get_step_order()
        self.GetParent().recording_document.reorder_steps(new_order)
        RecordingPersistence.save_to_disk(self.GetParent().recording_document)

        wx.CallAfter(self._edit_new_step, new_item)

        return True

    def _edit_new_step(self, item):
        """Opens edit dialog for a newly created step."""

        if not self.controller:
            return

        success = self.controller.edit_step_item(item)

        if not success:
            self.Delete(item)

    def _add_step_entry(self, parent, text, icon, step_data):
        """Creates a step entry node.

        Args:
            parent: Parent tree item.
            text: Display text.
            icon: Icon index.
            step_data: Associated step metadata.

        Returns:
            wx.TreeItemId: Created tree item.
        """
        item = self.AppendItem(parent, text)
        self.SetItemImage(item, icon)

        self.SetItemData(item, step_data)

        return item

    def set_step_status(self, index: int, status: StepStatus):
        """Updates the icon of a step based on its status.

        Args:
            index: Tree item index.
            status: New step status.
        """
        item = self.find_item_by_index(index)
        if not item or not item.IsOk():
            return

        icon = self._status_icons.get(status, -1)

        if icon == -1:
            self.SetItemImage(item, -1)
        else:
            self.SetItemImage(item, icon)

        self.EnsureVisible(item)

    def reset_statuses(self):
        """Resets all step nodes to NOT_RUN status."""

        def walk(parent):
            child, cookie = self.GetFirstChild(parent)

            while child.IsOk():

                if self.GetItemData(child):  # step node
                    self.SetItemImage(child, self._status_icons[StepStatus.NOT_RUN])

                walk(child)

                child, cookie = self.GetNextChild(parent, cookie)

        walk(self.root)

    def clear(self):
        """Clears all tree items and re-initialises the root."""
        self.DeleteAllItems()

        self.root = self.AddRoot("Steps")

    def iter_steps(self):
        """
        Iterate over all step nodes in tree order.

        Yields:
            tuple(wx.TreeItemId, dict): (item, step_data)
        """

        def walk(parent):
            child, cookie = self.GetFirstChild(parent)

            while child.IsOk():
                data = self.GetItemData(child)

                if data:
                    yield child, data

                yield from walk(child)

                child, cookie = self.GetNextChild(parent, cookie)

        yield from walk(self.root)

    def find_item_by_index(self, index):
        """Finds a tree item by its associated index.

        Iterates through all steps and returns the first item whose data
        contains a matching "index" value.

        Args:
            index (int): The index to search for.

        Returns:
            Optional[wx.TreeItemId]: The matching tree item if found, otherwise None.
        """
        for item, data in self.iter_steps():
            if data.get("index") == index:
                return item
        return None

    def _create_images(self):
        """Initializes and assigns status icons to the tree.

        Creates an image list and maps step statuses to corresponding icons.
        """

        self.images = wx.ImageList(16, 16)

        self._icon_not_run = self.images.Add(
            wx.ArtProvider.GetBitmap(wx.ART_QUESTION, wx.ART_OTHER, (16, 16)))

        self._icon_running = self.images.Add(
            wx.ArtProvider.GetBitmap(wx.ART_GO_FORWARD, wx.ART_OTHER, (16, 16)))

        self._icon_pass = self.images.Add(
            wx.ArtProvider.GetBitmap(wx.ART_TICK_MARK, wx.ART_OTHER, (16, 16)))

        self._icon_fail = self.images.Add(
            wx.ArtProvider.GetBitmap(wx.ART_CROSS_MARK, wx.ART_OTHER, (16, 16)))

        self._icon_warning = self.images.Add(
            wx.ArtProvider.GetBitmap(wx.ART_WARNING, wx.ART_OTHER, (16, 16)))

        self.AssignImageList(self.images)

        self._status_icons = {
            StepStatus.NOT_RUN: self._icon_not_run,
            StepStatus.RUNNING: self._icon_running,
            StepStatus.PASSED: self._icon_pass,
            StepStatus.FAILED: self._icon_fail,
            StepStatus.WARNING: self._icon_warning
        }

    def _on_begin_drag(self, evt):
        """Handles the start of a drag operation for a tree item.

        Prevents dragging of the root item.

        Args:
            evt (wx.TreeEvent): The drag event.
        """
        item = evt.GetItem()

        if item == self.root:
            return

        self.drag_item = item
        evt.Allow()

    def _on_end_drag(self, _evt):
        """Handles drag-and-drop reordering of tree items.

        Moves the dragged item to a valid drop target, preserving its data
        and children. Invalid drops are ignored.
        """
        self._clear_drop_indicator()

        if not self.drag_item:
            return

        target = self._get_drop_target()

        if not self._is_valid_drop(target):
            self.drag_item = None
            return

        item_data = self._extract_item(self.drag_item)

        drop_point = self.ScreenToClient(wx.GetMousePosition())
        new_item = self._reinsert_item(target, item_data, drop_point=drop_point)

        self._restore_children(new_item, item_data["children"])

        self._finalise_drop(new_item, item_data)

    def _get_drop_target(self):
        """Determines the tree item under the current mouse position.

        Returns:
            wx.TreeItemId: The item under the cursor.
        """
        pos = self.ScreenToClient(wx.GetMousePosition())
        target, _ = self.HitTest(pos)
        return target

    def _is_valid_drop(self, target):
        """Checks whether a drop target is valid.

        A valid target must:
            - Exist
            - Not be the dragged item itself
            - Not be a descendant of the dragged item

        Args:
            target (wx.TreeItemId): The potential drop target.

        Returns:
            bool: True if the drop is valid, False otherwise.
        """
        if not target.IsOk():
            return False

        if target == self.drag_item:
            return False

        if self._is_descendant(self.drag_item, target):
            return False

        return True

    def _extract_item(self, item):
        """Extracts item data and removes it from the tree.

        Captures the item's visual and data properties, along with its
        immediate children, then deletes the item.

        Args:
            item (wx.TreeItemId): The item to extract.

        Returns:
            dict: A dictionary containing item properties and children.
        """
        data = {
            "text": self.GetItemText(item),
            "icon": self.GetItemImage(item),
            "data": self.GetItemData(item),
            "bold": self.IsBold(item),
            "expanded": self.IsExpanded(item),
            "children": []
        }

        child, cookie = self.GetFirstChild(item)

        while child.IsOk():
            data["children"].append((
                self.GetItemText(child),
                self.GetItemImage(child),
                self.GetItemData(child),
                self.IsBold(child)
            ))
            child, cookie = self.GetNextChild(item, cookie)

        self.Delete(item)

        return data

    def _reinsert_item(self, target, item_data, drop_point=None):
        """Reinserts an item into the tree at a new position.

        Determines whether to insert as a child or sibling based on the
        drop location, then applies stored styling.

        Args:
            target (wx.TreeItemId): The drop target item.
            item_data (dict): The extracted item data.
            drop_point (Optional[wx.Point]): Drop location in client
                coordinates. If not provided, the current mouse position is
                used.

        Returns:
            wx.TreeItemId: The newly created tree item.
        """
        text = item_data["text"]

        if drop_point is None:
            drop_point = self.ScreenToClient(wx.GetMousePosition())

        if not self.GetItemData(target) or target == self.root:
            parent = target
            new_item = self.AppendItem(parent, text)
        else:
            parent = self.GetItemParent(target)
            rect = self.GetBoundingRect(target)
            insert_after = drop_point.y > rect.y + rect.height / 2

            if insert_after:
                new_item = self.InsertItem(parent, target, text)
            else:
                prev = self.GetPrevSibling(target)
                if prev.IsOk():
                    new_item = self.InsertItem(parent, prev, text)
                else:
                    new_item = self.PrependItem(parent, text)

        self._apply_item_style(new_item, item_data)

        return new_item

    def _apply_item_style(self, item, item_data):
        """Applies stored visual and data properties to a tree item.

        Args:
            item (wx.TreeItemId): The item to style.
            item_data (dict): The stored item properties.
        """
        if item_data["icon"] != -1:
            self.SetItemImage(item, item_data["icon"])

        self.SetItemData(item, item_data["data"])

        if item_data["bold"]:
            self.SetItemBold(item)

    def _restore_children(self, parent, children):
        for t, i, d, b in children:
            c = self.AppendItem(parent, t)

            if i != -1:
                self.SetItemImage(c, i)

            self.SetItemData(c, d)

            if b:
                self.SetItemBold(c)

    def _finalise_drop(self, new_item, item_data):
        self.drag_item = None

        parent = self.GetItemParent(new_item)
        self.Expand(parent)

        if item_data["expanded"]:
            self.Expand(new_item)

        # Sync document
        new_order = self._get_step_order()
        self.GetParent().recording_document.reorder_steps(new_order)

        RecordingPersistence.save_to_disk(self.GetParent().recording_document)

    def _get_step_order(self) -> list:
        """Returns step data in current tree order.

        Returns:
            list: Ordered list of step metadata dictionaries.
        """
        order = []

        def walk(parent):
            child, cookie = self.GetFirstChild(parent)

            while child.IsOk():
                data = self.GetItemData(child)

                if data:  # step node
                    order.append(data)

                walk(child)
                child, cookie = self.GetNextChild(parent, cookie)

        walk(self.root)
        return order

    def _is_descendant(self, parent, child):
        """Checks if a node is a descendant of another.

        Args:
            parent: Potential ancestor node.
            child: Node to test.

        Returns:
            bool: True if child is within parent's subtree.
        """
        item = child

        while item.IsOk():

            if item == parent:
                return True

            item = self.GetItemParent(item)

        return False

    def _on_mouse_move(self, evt):
        """Handles mouse movement for drag visuals and hover detection."""

        if self.drag_item:
            pos = evt.GetPosition()
            item, _ = self.HitTest(pos)

            if item.IsOk():
                rect = self.GetBoundingRect(item)
                self.drop_indicator_y = rect.y + rect.height // 2
                self.Refresh()

        pos = evt.GetPosition()

        item, _ = self.HitTest(pos)

        if not item.IsOk():
            self.hover_timer.Stop()
            self.pending_hover_item = None
            self._info_overlay.Hide()
            self.hover_item = None
            evt.Skip()
            return

        data = self.GetItemData(item)

        # group node, not a real step
        if not data:
            self.hover_timer.Stop()
            self.pending_hover_item = None
            self._info_overlay.Hide()
            self.hover_item = None
            evt.Skip()
            return

        # already showing this item
        if item == self.hover_item:
            evt.Skip()
            return

        # remember candidate hover item and restart timer
        self.pending_hover_item = item
        self.hover_timer.StartOnce(75)

        evt.Skip()

    def _on_mouse_leave(self, evt):
        """Handles mouse leaving the control."""
        self.hover_timer.Stop()
        self.pending_hover_item = None
        self._info_overlay.Hide()

        self.hover_item = None

        evt.Skip()

    def _on_hover_timer(self, _evt):
        """Displays step information overlay after hover delay."""
        item = self.pending_hover_item

        if not item or not item.IsOk():
            return

        data = self.GetItemData(item)

        if not data:
            return

        self.hover_item = item

        self._info_overlay.update(data)

        pos = self.ScreenToClient(wx.GetMousePosition())
        screen_pos = self.ClientToScreen(pos)
        screen_pos.y += 20

        self._info_overlay.Position(screen_pos, (0, 0))
        self._info_overlay.Popup()

    def _on_paint(self, evt):
        """Handles custom drawing (drop indicator)."""
        evt.Skip()

        if self.drop_indicator_y is None:
            return

        wx.CallAfter(self._draw_drop_indicator)

    def _draw_drop_indicator(self):
        """Draws the drag-and-drop insertion line."""

        if self.drop_indicator_y is None:
            return

        dc = wx.ClientDC(self)

        dc.SetPen(wx.Pen(wx.Colour(0, 120, 215), 2))

        width, _ = self.GetClientSize()

        dc.DrawLine(0, self.drop_indicator_y, width, self.drop_indicator_y)

    def _clear_drop_indicator(self):
        """Clears the drop indicator line."""
        if self.drop_indicator_y is not None:
            self.drop_indicator_y = None
            self.Refresh()

    def _on_item_collapsed(self, event):
        """Prevents collapsing the root node."""
        item = event.GetItem()

        if item == self.GetRootItem():
            wx.CallAfter(self.Expand, item)  # re-expand after event finishes

        event.Skip()
