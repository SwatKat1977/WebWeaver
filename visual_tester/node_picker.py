"""
Copyright (C) 2025  Web Weaver Development Team
SPDX-License-Identifier: GPL-3.0-or-later

This file is part of Web Weaver (https://github.com/SwatKat1977/WebWeaver).
See the LICENSE file in the project root for full license details.
"""
import wx
from node_types import NODE_TYPES
from node_types import NodeCategory


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
            name for name, t in NODE_TYPES.items()
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
        t = NODE_TYPES[name]

        # Selection highlight
        if self.IsSelected(n):
            dc.SetBrush(wx.Brush(wx.Colour(255, 140, 0, 60)))
            dc.SetPen(wx.TRANSPARENT_PEN)
            dc.DrawRoundedRectangle(rect.x, rect.y, rect.width, rect.height, 4)

        # Colour swatch
        colour = wx.Colour(*t.color)
        dc.SetBrush(wx.Brush(colour))
        dc.SetPen(wx.Pen(wx.Colour(0, 0, 0), 1))
        dc.DrawRectangle(rect.x + 8, rect.y + 5, 16, rect.height - 10)

        # Label
        dc.SetTextForeground(wx.Colour(240, 240, 240))
        dc.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
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

class NodePicker(wx.MiniFrame):
    """Popup dialog for creating new nodes.

    Cross-platform version of the Unreal-style node picker.
    Provides a searchable list of node types with gradient background,
    proper focus handling, and consistent positioning.
    """

    def __init__(self, parent, position, add_callback):
        """Initialise the popup window and its UI components.

        Args:
            parent (wx.Window): Parent window to attach the popup to.
            position (wx.Point | wx.RealPoint): Screen position where the popup appears.
            add_callback (Callable): Function called when a node type is chosen.
        """
        super().__init__(
            parent,
            title="",
            style=wx.FRAME_NO_TASKBAR | wx.STAY_ON_TOP | wx.BORDER_NONE
        )
        self.add_callback = add_callback
        self._parent = parent

        # Ensure proper background and paint handling
        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        self.Bind(wx.EVT_PAINT, self._on_paint)

        # position is already in screen coordinates — just move
        if isinstance(position, wx.RealPoint):
            position = wx.Point(int(position.x), int(position.y))
        elif isinstance(position, tuple):
            position = wx.Point(int(position[0]), int(position[1]))
        self.Move(position)

        # --- Main layout ---
        panel = wx.Panel(self, style=wx.TAB_TRAVERSAL)
        panel.SetBackgroundColour(wx.Colour(0, 0, 0, 0))
        vbox = wx.BoxSizer(wx.VERTICAL)

        # Search box
        self.search = wx.SearchCtrl(panel, style=wx.TE_PROCESS_ENTER)
        self.search.ShowCancelButton(True)
        vbox.Add(self.search, 0, wx.EXPAND | wx.ALL, 6)

        # Node list
        self.listbox = NodeList(panel, self.on_pick)
        vbox.Add(self.listbox, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 6)

        panel.SetSizer(vbox)
        panel.Layout()

        self.listbox.update_filter("")
        panel.FitInside()
        panel.SetMinSize((260, 220))
        panel.Fit()
        self.SetClientSize(panel.GetSize())
        self.Layout()

        # --- Bindings ---
        self.search.Bind(wx.EVT_TEXT, self.on_filter)
        self.search.Bind(wx.EVT_KEY_DOWN, self.on_key)
        self.listbox.Bind(wx.EVT_KEY_DOWN, self.on_key)
        self.Bind(wx.EVT_SHOW, self.on_show)
        self.Bind(wx.EVT_ACTIVATE, self.on_activate)

        # Track clicks outside window (to dismiss)
        self.Bind(wx.EVT_KILL_FOCUS, self._on_focus_lost)

        # Give focus to the search box once shown
        wx.CallLater(50, self.search.SetFocus)

    # ---- Drawing rounded popup background ----
    def _on_paint(self, _event):
        """Handle paint events for the popup background."""
        dc = wx.AutoBufferedPaintDC(self)
        gc = wx.GraphicsContext.Create(dc)

        w, h = self.GetClientSize()
        path = gc.CreatePath()
        path.AddRoundedRectangle(0, 0, w, h, 8)

        # Shadow
        gc.SetBrush(wx.Brush(wx.Colour(0, 0, 0, 80)))
        gc.DrawRoundedRectangle(4, 4, w - 4, h - 4, 8)

        # Gradient background
        grad = gc.CreateLinearGradientBrush(
            0, 0, 0, h,
            wx.Colour(45, 46, 50),
            wx.Colour(35, 36, 40)
        )
        gc.SetBrush(grad)
        gc.SetPen(wx.Pen(wx.Colour(80, 80, 80)))
        gc.DrawPath(path)

    # ---- Logic ----
    def on_filter(self, _event):
        """Filter node types as the user types into the search box."""
        self.listbox.update_filter(self.search.GetValue())

    def on_key(self, event):
        """Handle keyboard navigation and selection."""
        code = event.GetKeyCode()
        sel = self.listbox.GetSelection()

        if code in (wx.WXK_RETURN, wx.WXK_NUMPAD_ENTER):
            self.on_pick(sel)
        elif code == wx.WXK_UP and sel > 0:
            self.listbox.SetSelection(sel - 1)
        elif code == wx.WXK_DOWN and sel < len(self.listbox.filtered) - 1:
            self.listbox.SetSelection(sel + 1)
        elif code == wx.WXK_ESCAPE:
            self.Close()
        else:
            event.Skip()

    def on_pick(self, sel):
        """Handle node selection and trigger the add callback."""
        if isinstance(sel, int):
            if sel < 0 or sel >= len(self.listbox.filtered):
                return
            node_type = self.listbox.filtered[sel]
        else:
            node_type = sel
        self.add_callback(node_type, self.GetPosition())
        self.Close()

    def on_show(self, event):
        """Ensure search box focus after showing."""
        if event.IsShown():
            wx.CallLater(50, self.search.SetFocus)
        event.Skip()

    def on_activate(self, event):
        """Refocus when reactivated."""
        if event.GetActive():
            wx.CallLater(50, self.search.SetFocus)
        event.Skip()

    def _on_focus_lost(self, _event):
        """Dismiss when losing focus (simulate transient popup behaviour)."""
        if not self.IsActive():
            self.Close()
