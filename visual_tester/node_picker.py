import wx
from node_types import NODE_TYPES


class NodeList(wx.VListBox):
    """Custom list displaying node types with coloured squares."""

    def __init__(self, parent, on_select):
        super().__init__(parent, style=wx.BORDER_SIMPLE)
        self.on_select = on_select
        self.nodes = list(NODE_TYPES.keys())
        self.filtered = self.nodes
        self.SetItemCount(len(self.filtered))
        self.Bind(wx.EVT_LEFT_DCLICK, self.on_double_click)

    def update_filter(self, text):
        ft = text.lower().strip()
        self.filtered = [name for name in self.nodes if not ft or ft in name.lower()]
        self.SetItemCount(len(self.filtered))
        self.RefreshAll()
        if self.filtered:
            self.SetSelection(0)

    def OnMeasureItem(self, n):
        return 24  # item height

    def OnDrawItem(self, dc, rect, n):
        if n < 0 or n >= len(self.filtered):
            return
        name = self.filtered[n]
        t = NODE_TYPES[name]

        # Background highlight
        if self.IsSelected(n):
            dc.SetBrush(wx.Brush(wx.Colour(255, 140, 0, 40)))
            dc.SetPen(wx.TRANSPARENT_PEN)
            dc.DrawRectangle(rect)

        # Draw colour box
        colour = wx.Colour(*t.color)
        dc.SetBrush(wx.Brush(colour))
        dc.SetPen(wx.Pen(wx.Colour(0, 0, 0), 1))
        dc.DrawRectangle(rect.x + 6, rect.y + 4, 16, rect.height - 8)

        # Draw node name
        dc.SetTextForeground(wx.Colour(240, 240, 240))
        dc.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        dc.DrawText(name, rect.x + 28, rect.y + 4)

    def on_double_click(self, event):
        sel = self.GetSelection()
        if sel != wx.NOT_FOUND:
            name = self.filtered[sel]
            self.on_select(name)


class NodePicker(wx.PopupTransientWindow):
    """Popup search dialog for adding nodes."""
    def __init__(self, parent, position, add_callback):
        super().__init__(parent, wx.BORDER_SIMPLE)
        self.add_callback = add_callback
        self.position = position

        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        self.search = wx.SearchCtrl(panel, style=wx.TE_PROCESS_ENTER)
        self.search.ShowCancelButton(True)
        vbox.Add(self.search, 0, wx.EXPAND | wx.ALL, 4)

        self.listbox = NodeList(panel, self.on_pick)
        vbox.Add(self.listbox, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 4)

        panel.SetSizer(vbox)
        panel.Fit()
        self.SetClientSize(panel.GetBestSize())
        self.Layout()

        panel.SetSizer(vbox)
        panel.Layout()

        # Size logic fix
        self.listbox.update_filter("")  # ensure it has content before sizing
        panel.FitInside()
        panel.SetMinSize((240, 200))  # give it a base width/height
        panel.Fit()
        self.SetClientSize(panel.GetSize())
        self.Layout()

        self.search.Bind(wx.EVT_TEXT, self.on_filter)
        self.Bind(wx.EVT_CHAR_HOOK, self.on_key)

        self.listbox.update_filter("")

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
