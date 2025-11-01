"""
Copyright (C) 2025  Web Weaver Development Team
SPDX-License-Identifier: GPL-3.0-or-later

This file is part of Web Weaver (https://github.com/SwatKat1977/WebWeaver).
See the LICENSE file in the project root for full license details.
"""
import wx
from node_types import NODE_TYPES


# ----------------------------
#  Custom List
# ----------------------------

class NodeList(wx.VListBox):
    """Custom list displaying node types with coloured squares."""
    def __init__(self, parent, on_select):
        super().__init__(parent, style=wx.BORDER_NONE)
        self.on_select = on_select
        self.nodes = list(NODE_TYPES.keys())
        self.filtered = self.nodes
        self.SetItemCount(len(self.filtered))
        self.Bind(wx.EVT_LEFT_DCLICK, self.on_double_click)
        self.SetBackgroundColour(wx.Colour(38, 39, 43))

    def update_filter(self, text):
        ft = text.lower().strip()
        self.filtered = [name for name in self.nodes if not ft or ft in name.lower()]
        self.SetItemCount(len(self.filtered))
        self.RefreshAll()
        if self.filtered:
            self.SetSelection(0)

    def OnMeasureItem(self, n):
        return 26  # row height

    def OnDrawItem(self, dc, rect, n):
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

    def on_double_click(self, event):
        sel = self.GetSelection()
        if sel != wx.NOT_FOUND:
            name = self.filtered[sel]
            self.on_select(name)


# ----------------------------
#  Node Picker Popup
# ----------------------------

class NodePicker(wx.PopupTransientWindow):
    """Unreal-style popup node creation dialog with rounded corners and shadow."""
    def __init__(self, parent, position, add_callback):
        super().__init__(parent, wx.BORDER_NONE)
        self.add_callback = add_callback
        self.position = position

        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        self.Bind(wx.EVT_PAINT, self.OnPaint)

        panel = wx.Panel(self, style=wx.TAB_TRAVERSAL)
        vbox = wx.BoxSizer(wx.VERTICAL)

        self.search = wx.SearchCtrl(panel, style=wx.TE_PROCESS_ENTER)
        self.search.ShowCancelButton(True)
        vbox.Add(self.search, 0, wx.EXPAND | wx.ALL, 6)

        self.listbox = NodeList(panel, self.on_pick)
        vbox.Add(self.listbox, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 6)

        panel.SetSizer(vbox)
        panel.Layout()

        # Populate list before sizing
        self.listbox.update_filter("")
        panel.FitInside()
        panel.SetMinSize((260, 220))
        panel.Fit()
        self.SetClientSize(panel.GetSize())
        self.Layout()

        self.search.Bind(wx.EVT_TEXT, self.on_filter)
        self.search.Bind(wx.EVT_KEY_DOWN, self.on_key)
        self.listbox.Bind(wx.EVT_KEY_DOWN, self.on_key)
        self.Bind(wx.EVT_SHOW, self.on_show)

        # Give focus to the search box immediately
        self.search.SetFocus()

        # Ensure search box focus when popup activates (macOS/Linux fix)

        self.Bind(wx.EVT_ACTIVATE, lambda e: (self.search.SetFocus(), e.Skip()))

    # ---- Drawing rounded popup background ----
    def OnPaint(self, event):
        dc = wx.AutoBufferedPaintDC(self)
        gc = wx.GraphicsContext.Create(dc)

        w, h = self.GetClientSize()
        path = gc.CreatePath()
        path.AddRoundedRectangle(0, 0, w, h, 8)

        # shadow
        gc.SetBrush(wx.Brush(wx.Colour(0, 0, 0, 80)))
        gc.DrawRoundedRectangle(4, 4, w - 4, h - 4, 8)

        # gradient background
        grad = gc.CreateLinearGradientBrush(0, 0, 0, h,
                                            wx.Colour(45, 46, 50),
                                            wx.Colour(35, 36, 40))
        gc.SetBrush(grad)  # Use gradient brush directly
        gc.SetPen(wx.Pen(wx.Colour(80, 80, 80)))
        gc.DrawPath(path)

    # ---- Logic ----
    def on_filter(self, event):
        self.listbox.update_filter(self.search.GetValue())

    def on_key(self, event):
        code = event.GetKeyCode()
        sel = self.listbox.GetSelection()

        if code in (wx.WXK_RETURN, wx.WXK_NUMPAD_ENTER):
            self.on_pick(sel)
        elif code == wx.WXK_UP and sel > 0:
            self.listbox.SetSelection(sel - 1)
        elif code == wx.WXK_DOWN and sel < len(self.listbox.filtered) - 1:
            self.listbox.SetSelection(sel + 1)
        elif code == wx.WXK_ESCAPE:
            self.Dismiss()
        else:
            event.Skip()

    def on_pick(self, sel):
        if isinstance(sel, int):
            if sel < 0 or sel >= len(self.listbox.filtered):
                return
            node_type = self.listbox.filtered[sel]
        else:
            node_type = sel
        self.add_callback(node_type, self.position)
        self.Dismiss()

    def on_show(self, event):
        if event.IsShown():
            wx.CallAfter(self.search.SetFocus)
        event.Skip()
