import wx


class SendkeyKeySelectionDialog(wx.Dialog):

    KEY_CHOICES = [
        "ENTER", "TAB", "ESCAPE", "BACKSPACE", "DELETE",
        "SPACE", "ARROW_UP", "ARROW_DOWN",
        "ARROW_LEFT", "ARROW_RIGHT",
        "HOME", "END"
    ]

    def __init__(self, parent):

        super().__init__(parent, title="Select Key", size=(300, 250))

        panel = wx.Panel(self)
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # Key dropdown
        main_sizer.Add(wx.StaticText(panel, label="Key"), 0, wx.ALL, 5)

        self.key_choice = wx.Choice(panel, choices=self.KEY_CHOICES)
        self.key_choice.SetSelection(0)

        main_sizer.Add(self.key_choice, 0, wx.EXPAND | wx.ALL, 5)

        # Modifiers
        main_sizer.Add(wx.StaticText(panel, label="Modifiers"), 0, wx.ALL, 5)

        self.ctrl = wx.CheckBox(panel, label="CTRL")
        self.alt = wx.CheckBox(panel, label="ALT")
        self.shift = wx.CheckBox(panel, label="SHIFT")
        self.meta = wx.CheckBox(panel, label="META")

        main_sizer.Add(self.ctrl, 0, wx.ALL, 2)
        main_sizer.Add(self.alt, 0, wx.ALL, 2)
        main_sizer.Add(self.shift, 0, wx.ALL, 2)
        main_sizer.Add(self.meta, 0, wx.ALL, 2)

        # Buttons
        btn_sizer = wx.StdDialogButtonSizer()

        ok_btn = wx.Button(panel, wx.ID_OK)
        cancel_btn = wx.Button(panel, wx.ID_CANCEL)

        btn_sizer.AddButton(ok_btn)
        btn_sizer.AddButton(cancel_btn)
        btn_sizer.Realize()

        main_sizer.Add(btn_sizer, 0, wx.ALIGN_RIGHT | wx.ALL, 10)

        panel.SetSizer(main_sizer)

    def get_result(self):

        key = self.key_choice.GetStringSelection()

        modifiers = []

        if self.ctrl.GetValue():
            modifiers.append("CTRL")

        if self.alt.GetValue():
            modifiers.append("ALT")

        if self.shift.GetValue():
            modifiers.append("SHIFT")

        if self.meta.GetValue():
            modifiers.append("META")

        if modifiers:
            return key, "+".join(modifiers)

        return key, None