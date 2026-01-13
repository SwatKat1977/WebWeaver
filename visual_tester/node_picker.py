"""
Copyright (C) 2025  Web Weaver Development Team
SPDX-License-Identifier: GPL-3.0-or-later

This file is part of Web Weaver (https://github.com/SwatKat1977/WebWeaver).
See the LICENSE file in the project root for full license details.
"""
import wx
from node_type import NodeCategory
from node_registry import NodeRegistry


# ----------------------------
#  Custom List
# ----------------------------

class NodeList(wx.VListBox):
    """Custom list widget that displays available node types.

    Each entry is rendered with a small coloured square and label.
    The list supports filtering based on search text and triggers a
    callback when a node type is double-clicked.
    """

    def __init__(self, parent, on_select):
        """Initialise the node list.

        Args:
            parent (wx.Window): The parent window or panel.
            on_select (Callable): Callback invoked when a node type is selected.
        """
        super().__init__(parent, style=wx.BORDER_NONE)
        self.on_select = on_select
        # Exclude special node types (e.g. Start, End) from picker
        self.nodes = [
            name for name, t in NodeRegistry.all()
            if t.category == NodeCategory.NORMAL
        ]
        self.filtered = self.nodes
        self.SetItemCount(len(self.filtered))
        self.Bind(wx.EVT_LEFT_DCLICK, self.on_double_click)
        self.SetBackgroundColour(wx.Colour(38, 39, 43))

    def update_filter(self, text):
        """Filter visible node types based on search text.

        Args:
            text (str): Substring used to filter node names.
        """
        ft = text.lower().strip()
        self.filtered = [name for name in self.nodes if not ft or ft in name.lower()]
        self.SetItemCount(len(self.filtered))
        self.RefreshAll()
        if self.filtered:
            self.SetSelection(0)

    def OnMeasureItem(self, _n):
        """
        Return the height of each list row.
        Note: Disable pylint warning as this an overridden method.
        """
        # pylint: disable=invalid-name
        return 26  # row height

    def OnDrawItem(self, dc, rect, n):
        """Custom draw handler for rendering each node type entry.
           Note: Disable pylint warning as this an overridden method.

        Args:
            dc (wx.DC): The device context to draw with.
            rect (wx.Rect): The rectangle bounds for the item.
            n (int): The index of the item being drawn.
        """
        # pylint: disable=invalid-name
        if n < 0 or n >= len(self.filtered):
            return

        name = self.filtered[n]
        t = NodeRegistry.get(name)

        # --- Row background (this removes the white) ---
        dc.SetBrush(wx.Brush(wx.Colour(30, 30, 35)))
        dc.SetPen(wx.TRANSPARENT_PEN)
        dc.DrawRectangle(rect.x, rect.y, rect.width, rect.height)

        # Selection highlight
        if self.IsSelected(n):
            dc.SetBrush(wx.Brush(wx.Colour(255, 140, 0, 160)))
            dc.SetPen(wx.TRANSPARENT_PEN)
            dc.DrawRoundedRectangle(rect.x, rect.y, rect.width, rect.height, 4)

        # Colour swatch
        swatch = wx.Colour(*t.colour)
        dc.SetBrush(wx.Brush(swatch))
        dc.SetPen(wx.Pen(wx.Colour(0, 0, 0)))
        dc.DrawRectangle(rect.x + 8, rect.y + 5, 16, rect.height - 10)

        # Text style - make disabled options a muted text
        is_disabled = (t.category != NodeCategory.NORMAL)

        if is_disabled:
            text_colour = wx.Colour(110, 110, 110)
        else:
            text_colour = wx.Colour(240, 240, 240)

        # Label
        dc.SetTextForeground(text_colour)
        dc.SetFont(wx.Font(10,
                           wx.FONTFAMILY_DEFAULT,
                           wx.FONTSTYLE_NORMAL,
                           wx.FONTWEIGHT_NORMAL))
        dc.DrawText(name, rect.x + 30, rect.y + 5)

    def on_double_click(self, _event):
        """Handle double-click events and trigger the selection callback."""

        sel = self.GetSelection()
        if sel != wx.NOT_FOUND:
            name = self.filtered[sel]
            self.on_select(name)


# ----------------------------
#  Node Picker Popup
# ----------------------------

class NodePicker(wx.Frame):
    """Popup dialog for creating new nodes with full keyboard support."""

    def __init__(self, parent, position, add_callback):
        style = wx.FRAME_NO_TASKBAR | wx.STAY_ON_TOP | wx.BORDER_NONE

        super().__init__(parent, title="", style=style)
        self.add_callback = add_callback

        # MOVE TO POSITION
        if isinstance(position, wx.RealPoint):
            position = wx.Point(int(position.x), int(position.y))
        elif isinstance(position, tuple):
            position = wx.Point(int(position[0]), int(position[1]))
        self.Move(position)

        # PANEL + BACKGROUND
        bg = wx.Colour(30, 30, 35)
        panel = wx.Panel(self, style=wx.BORDER_NONE | wx.FULL_REPAINT_ON_RESIZE)
        panel.SetBackgroundColour(bg)

        vbox = wx.BoxSizer(wx.VERTICAL)

        # SEARCH BOX
        self.search = wx.SearchCtrl(panel, style=wx.TE_PROCESS_ENTER)
        self.search.SetForegroundColour(wx.Colour(230, 230, 230))
        self.search.SetBackgroundColour(bg)
        vbox.Add(self.search, 0, wx.EXPAND | wx.ALL, 6)

        # LIST
        self.scroller = wx.ScrolledWindow(panel, style=wx.BORDER_NONE)
        self.scroller.SetBackgroundColour(bg)
        self.scroller.SetScrollRate(0, 10)

        # IMPORTANT: listbox parent must be scroller, not panel
        self.listbox = NodeList(self.scroller, self.on_pick)

        s2 = wx.BoxSizer(wx.VERTICAL)
        s2.Add(self.listbox, 1, wx.EXPAND)
        self.scroller.SetSizer(s2)

        vbox.Add(self.scroller, 1, wx.EXPAND)

        panel.SetSizer(vbox)
        panel.SetAutoLayout(True)

        # SIZING
        panel.Layout()
        panel.Fit()
        self.Fit()

        w, h = panel.GetSize()
        self.SetClientSize(wx.Size(max(260, w), h))  # enforce min width but allow growing

        wx.CallAfter(self._resize_to_content)

        self.Bind(wx.EVT_SIZE, self._on_resize)

        # FILTERING
        self.search.Bind(wx.EVT_TEXT, self.on_filter)
        self.Bind(wx.EVT_KEY_DOWN, self.on_key)

        # CLOSE WHEN LOSING FOCUS
        self.Bind(wx.EVT_ACTIVATE, self._on_activate)

        # Give focus
        wx.CallLater(10, self.search.SetFocus)

    def _on_activate(self, event):
        """Close when clicking outside (behaves like popup)"""
        if not event.GetActive():
            self.Close()
        event.Skip()

    def _resize_to_content(self):
        """Resize popup height based on number of items."""
        row_height = self.listbox.OnMeasureItem(0)
        rows = len(self.listbox.filtered)
        max_rows = 8

        visible_rows = min(rows, max_rows)

        search_h = self.search.GetSize().height

        height = search_h + (visible_rows * row_height) + 12  # tight margin

        self.SetClientSize(wx.Size(300, height))

        # ensure scroller knows full height if scrolling needed
        total_height = (rows * row_height) + 6
        self.scroller.SetVirtualSize(wx.Size(-1, total_height))

    def on_filter(self, _event):
        self.listbox.update_filter(self.search.GetValue())
        self._resize_to_content()

    def on_key(self, event):
        code = event.GetKeyCode()

        # ENTER selects
        if code in (wx.WXK_RETURN, wx.WXK_NUMPAD_ENTER):
            sel = self.listbox.GetSelection()
            self.on_pick(sel)

        # ESC closes
        elif code == wx.WXK_ESCAPE:
            self.Close()

        # Otherwise allow normal typing
        else:
            event.Skip()

    def on_pick(self, sel):
        if isinstance(sel, int):
            if sel < 0 or sel >= len(self.listbox.filtered):
                return
            node_type = self.listbox.filtered[sel]
        else:
            node_type = sel

        self.add_callback(node_type, self.GetPosition())
        self.Close()

    def _on_resize(self, _event):
        size = self.GetClientSize()

        panel = self.GetChildren()[0]
        panel.SetSize(size)

        # resize listbox explicitly
        self.listbox.SetSize(size)

        self.Layout()
