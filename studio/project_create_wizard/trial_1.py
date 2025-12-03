import wx
from wizard_web_select_browser_page import WizardWebSelectApplicationDialog


# Test harness
class TestFrame(wx.Frame):
    def __init__(self):
        super().__init__(None, title="Scroll Demo")
        btn = wx.Button(self, label="Show Dialog")
        btn.Bind(wx.EVT_BUTTON, self.open_dialog)
        self.Show()

    def open_dialog(self, _):
        dlg = WizardWebSelectApplicationDialog(self)
        dlg.ShowModal()
        dlg.Destroy()


if __name__ == "__main__":
    app = wx.App(False)
    TestFrame()
    app.MainLoop()
