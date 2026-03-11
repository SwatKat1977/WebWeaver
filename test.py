import wx


class DialogHeader(wx.Panel):
    def __init__(self, parent, title, description, icon=wx.ART_INFORMATION):
        super().__init__(parent)

        main = wx.BoxSizer(wx.HORIZONTAL)

        bmp = wx.ArtProvider.GetBitmap(icon, wx.ART_OTHER, (32, 32))
        icon_ctrl = wx.StaticBitmap(self, bitmap=bmp)

        text_sizer = wx.BoxSizer(wx.VERTICAL)

        title_text = wx.StaticText(self, label=title)
        font = title_text.GetFont()
        font.MakeBold()
        font.SetPointSize(font.GetPointSize() + 4)
        title_text.SetFont(font)

        desc_text = wx.StaticText(self, label=description)

        text_sizer.Add(title_text, 0, wx.BOTTOM, 4)
        text_sizer.Add(desc_text, 0)

        main.Add(icon_ctrl, 0, wx.ALL | wx.ALIGN_TOP, 12)
        main.Add(text_sizer, 1, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 12)

        self.SetSizer(main)


class FancyDialogBase(wx.Dialog):

    def __init__(self, parent, title, header_title, header_desc):
        super().__init__(parent, title=title)

        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # Header
        header = DialogHeader(self, header_title, header_desc)
        main_sizer.Add(header, 0, wx.EXPAND)

        # Divider
        line = wx.StaticLine(self)
        main_sizer.Add(line, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 5)

        # Content area
        self.content = wx.Panel(self)
        self.content_sizer = wx.FlexGridSizer(cols=2, hgap=10, vgap=10)
        self.content_sizer.AddGrowableCol(1)

        self.content.SetSizer(self.content_sizer)

        main_sizer.Add(self.content, 1, wx.EXPAND | wx.ALL, 15)

        # Buttons
        btn_sizer = self.CreateButtonSizer(wx.OK | wx.CANCEL)
        main_sizer.Add(btn_sizer, 0, wx.ALL | wx.ALIGN_RIGHT, 10)

        self.SetSizer(main_sizer)

        self.Bind(wx.EVT_BUTTON, self._on_ok, id=wx.ID_OK)

    def add_field(self, label, control):
        self.content_sizer.Add(
            wx.StaticText(self.content, label=label),
            0, wx.ALIGN_CENTER_VERTICAL,
            5)

        ctrl = control(self.content)

        self.content_sizer.Add(ctrl, 1, wx.EXPAND)

        return ctrl

    def add_help(self, text):
        box = wx.StaticBox(self, label="Tips")
        sizer = wx.StaticBoxSizer(box, wx.VERTICAL)

        tip = wx.StaticText(self, label=text)
        tip.Wrap(350)

        sizer.Add(tip, 0, wx.ALL, 8)

        self.GetSizer().Insert(2, sizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 10)

    def _validate(self):
        return True

    def _on_ok(self, event):
        if self._validate():
            self.EndModal(wx.ID_OK)


class ClickStepEditor(FancyDialogBase):

    def __init__(self, parent):
        super().__init__(
            parent,
            "Edit Click Step",
            "Edit Click Step",
            "Configure how the automation performs a click.")

        # Add help panel here
        self.add_help(
            "XPath should uniquely identify the element.\n"
            "Example: //button[@id='login']")

        self.step_label = self.add_field("Step Label:", wx.TextCtrl)
        self.xpath = self.add_field("XPath:", wx.TextCtrl)

        self.Layout()
        self.Fit()
        self.SetMinSize(self.GetSize())

    def _validate(self):

        if not self.xpath.GetValue():
            wx.MessageBox("XPath cannot be empty", "Validation error")
            return False

        return True


class DemoFrame(wx.Frame):
    def __init__(self):
        super().__init__(None, title="Demo")

        btn = wx.Button(self, label="Open Step Editor")
        btn.Bind(wx.EVT_BUTTON, self.open_dialog)

        s = wx.BoxSizer(wx.VERTICAL)
        s.Add(btn, 0, wx.ALL, 20)

        self.SetSizer(s)
        self.SetSize((300, 200))

    def open_dialog(self, event):

        dlg = ClickStepEditor(self)

        dlg.ShowModal()
        dlg.Destroy()


app = wx.App()
frame = DemoFrame()
frame.Show()
app.MainLoop()
