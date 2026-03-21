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
from enum import Enum
import wx
from webweaver.studio.ui.step_information_overlay import StepInformationOverlay


class StepStatus(Enum):
    NOT_RUN = 0
    RUNNING = 1
    PASSED = 2
    FAILED = 3
    WARNING = 4


class RecordingStepTree(wx.TreeCtrl):

    def __init__(self, parent):
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

        self.ExpandAll()

    @property
    def tree_root(self) -> wx.TreeItemId:
        return self.root

    def add_step(self,
                  label: str, data: dict,
                  parent: wx.TreeItemId = None) -> None:
        parent_node = self.root if parent is None else parent
        self._add_step_entry(parent_node, label, self._icon_not_run, data)
        self.Expand(self.root)

    def add_group(self,
                  parent: wx.TreeItemId,
                  label: str) -> wx.TreeItemId:
        group_item_id = self.AppendItem(parent, label)
        self.SetItemBold(group_item_id)
        return group_item_id

    def _add_step_entry(self, parent, text, icon, step_data):

        item = self.AppendItem(parent, text)
        self.SetItemImage(item, icon)

        self.SetItemData(item, step_data)

        return item

    def set_step_status(self, item, status: StepStatus):

        if not item or not item.IsOk():
            return

        icon = self._status_icons.get(status, -1)

        if icon == -1:
            self.SetItemImage(item, -1)
        else:
            self.SetItemImage(item, icon)

    def reset_statuses(self):

        def walk(parent):

            child, cookie = self.GetFirstChild(parent)

            while child.IsOk():

                if self.GetItemData(child):  # step node
                    self.SetItemImage(child, self._status_icons[StepStatus.NOT_RUN])

                walk(child)

                child, cookie = self.GetNextChild(parent, cookie)

        walk(self.root)

    def clear(self):
        self.DeleteAllItems()

        self.root = self.AddRoot("Steps")

    def _create_images(self):

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

        item = evt.GetItem()

        if item == self.root:
            return

        self.drag_item = item
        evt.Allow()

    def _on_end_drag(self, _evt):

        self._clear_drop_indicator()

        if not self.drag_item:
            return

        pos = self.ScreenToClient(wx.GetMousePosition())
        target, flags = self.HitTest(pos)

        if not target.IsOk():
            self.drag_item = None
            return

        if target == self.drag_item:
            self.drag_item = None
            return

        if self._is_descendant(self.drag_item, target):
            self.drag_item = None
            return

        text = self.GetItemText(self.drag_item)
        icon = self.GetItemImage(self.drag_item)
        data = self.GetItemData(self.drag_item)
        bold = self.IsBold(self.drag_item)
        expanded = self.IsExpanded(self.drag_item)

        # save children
        children = []
        child, cookie = self.GetFirstChild(self.drag_item)

        while child.IsOk():
            children.append((
                self.GetItemText(child),
                self.GetItemImage(child),
                self.GetItemData(child),
                self.IsBold(child)
            ))
            child, cookie = self.GetNextChild(self.drag_item, cookie)

        self.Delete(self.drag_item)

        # -------------------------
        # DROP ON GROUP
        # -------------------------
        if not self.GetItemData(target) or target == self.root:
            parent = target
            new_item = self.AppendItem(parent, text)

        else:
            parent = self.GetItemParent(target)

            rect = self.GetBoundingRect(target)
            insert_after = pos.y > rect.y + rect.height / 2

            if insert_after:
                new_item = self.InsertItem(parent, target, text)
            else:
                prev = self.GetPrevSibling(target)

                if prev.IsOk():
                    new_item = self.InsertItem(parent, prev, text)
                else:
                    new_item = self.PrependItem(parent, text)

        if icon != -1:
            self.SetItemImage(new_item, icon)

        self.SetItemData(new_item, data)

        if bold:
            self.SetItemBold(new_item)

        # restore children
        for t, i, d, b in children:
            c = self.AppendItem(new_item, t)

            if i != -1:
                self.SetItemImage(c, i)

            self.SetItemData(c, d)

            if b:
                self.SetItemBold(c)

        self.drag_item = None
        self.Expand(parent)

        # ensure moved groups stay expanded
        if expanded:
            self.Expand(new_item)

    def _is_descendant(self, parent, child):

        item = child

        while item.IsOk():

            if item == parent:
                return True

            item = self.GetItemParent(item)

        return False

    def _on_mouse_move(self, evt):

        if self.drag_item:
            pos = evt.GetPosition()
            item, flags = self.HitTest(pos)

            if item.IsOk():
                rect = self.GetBoundingRect(item)
                self.drop_indicator_y = rect.y + rect.height // 2
                self.Refresh()

        pos = evt.GetPosition()

        item, flags = self.HitTest(pos)

        if not item.IsOk():
            self.hover_timer.Stop()
            self.pending_hover_item = None
            self._info_overlay.Hide()
            self.hover_item = None
            self.UnselectAll()
            evt.Skip()
            return

        data = self.GetItemData(item)

        # group node, not a real step
        if not data:
            self.hover_timer.Stop()
            self.pending_hover_item = None
            self._info_overlay.Hide()
            self.hover_item = None
            self.UnselectAll()
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
        self.hover_timer.Stop()
        self.pending_hover_item = None
        self._info_overlay.Hide()
        self.hover_item = None
        self.UnselectAll()

        evt.Skip()

    def _on_hover_timer(self, _evt):
        item = self.pending_hover_item

        if not item or not item.IsOk():
            return

        data = self.GetItemData(item)

        if not data:
            return

        self.hover_item = item
        self.SelectItem(item)

        self._info_overlay.update(data)

        pos = self.ScreenToClient(wx.GetMousePosition())
        screen_pos = self.ClientToScreen(pos)
        screen_pos.y += 20

        self._info_overlay.Position(screen_pos, (0, 0))
        self._info_overlay.Popup()

    def _on_paint(self, evt):

        evt.Skip()

        if self.drop_indicator_y is None:
            return

        wx.CallAfter(self._draw_drop_indicator)

    def _draw_drop_indicator(self):

        if self.drop_indicator_y is None:
            return

        dc = wx.ClientDC(self)

        dc.SetPen(wx.Pen(wx.Colour(0, 120, 215), 2))

        width, _ = self.GetClientSize()

        dc.DrawLine(0, self.drop_indicator_y, width, self.drop_indicator_y)

    def _clear_drop_indicator(self):
        if self.drop_indicator_y is not None:
            self.drop_indicator_y = None
            self.Refresh()

    def _on_item_collapsed(self, event):
        item = event.GetItem()

        if item == self.GetRootItem():
            wx.CallAfter(self.Expand, item)  # re-expand after event finishes

        event.Skip()
