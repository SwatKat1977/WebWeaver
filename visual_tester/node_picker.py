import wx
from node_types import NODE_TYPES


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

        self.listbox = wx.ListBox(panel)
        vbox.Add(self.listbox, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 4)

        panel.SetSizer(vbox)
        self.SetClientSize(panel.GetBestSize())
        panel.Fit()
        self.nodes = list(NODE_TYPES.keys())
        self.update_list()

        self.search.Bind(wx.EVT_TEXT, self.on_filter)
        self.listbox.Bind(wx.EVT_LISTBOX_DCLICK, self.on_pick)
        self.Bind(wx.EVT_CHAR_HOOK, self.on_key)

        self.Layout()

    def update_list(self, filter_text=""):
        self.listbox.Clear()
        ft = filter_text.lower().strip()
        for name, t in NODE_TYPES.items():
            if not ft or ft in name.lower():
                display = f"{name}"
                self.listbox.Append(display, clientData=t)

        if self.listbox.GetCount() > 0:
            self.listbox.SetSelection(0)

    def on_filter(self, event):
        self.update_list(self.search.GetValue())

    def on_key(self, event):
        code = event.GetKeyCode()
        if code in (wx.WXK_RETURN, wx.WXK_NUMPAD_ENTER):
            self.on_pick(None)
        elif code == wx.WXK_ESCAPE:
            self.Dismiss()
        else:
            event.Skip()

    def on_pick(self, event):
        sel = self.listbox.GetSelection()
        if sel != wx.NOT_FOUND:
            t = self.listbox.GetClientData(sel)
            node_type = t.type_name
            self.add_callback(node_type, self.position)
        self.Dismiss()
