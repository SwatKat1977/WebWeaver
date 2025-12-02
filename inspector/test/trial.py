import wx
import wx.aui as aui

class MainFrame(wx.Frame):
    def __init__(self):
        super().__init__(None, title="Webweaver Studio", size=(1400, 900))

        # AUI Manager
        self._mgr = aui.AuiManager(self)

        # -------------------------
        # Projects panel (left top)
        # -------------------------
        project_panel = wx.Panel(self)
        project_sizer = wx.BoxSizer(wx.VERTICAL)
        project_sizer.Add(wx.StaticText(project_panel, label="Projects"), 0, wx.ALL, 5)
        project_tree = wx.TreeCtrl(project_panel, style=wx.TR_HAS_BUTTONS)
        project_sizer.Add(project_tree, 1, wx.EXPAND | wx.ALL, 5)
        project_panel.SetSizer(project_sizer)

        self._mgr.AddPane(
            project_panel,
            aui.AuiPaneInfo()
            .Left()                 # dock on the left side
            .Caption("Projects")
            .CloseButton(True)
            .MaximizeButton(True)
            .MinimizeButton(True)
            .BestSize(300, 300)
        )

        # -------------------------
        # Modules panel (left bottom)
        # -------------------------
        modules_panel = wx.Panel(self)
        modules_sizer = wx.BoxSizer(wx.VERTICAL)
        modules_sizer.Add(wx.StaticText(modules_panel, label="Modules"), 0, wx.ALL, 5)
        modules_tree = wx.TreeCtrl(modules_panel, style=wx.TR_HAS_BUTTONS)
        modules_sizer.Add(modules_tree, 1, wx.EXPAND | wx.ALL, 5)
        modules_panel.SetSizer(modules_sizer)

        self._mgr.AddPane(
            modules_panel,
            aui.AuiPaneInfo()
            .Left()
            .Caption("Modules")
            .CloseButton(True)
            .MaximizeButton(True)
            .MinimizeButton(True)
            .BestSize(300, 300)
            .Position(1)  # below the Projects panel
        )

        # -------------------------
        # Main workspace (center)
        # -------------------------
        main_panel = wx.Panel(self)
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(wx.StaticText(main_panel, label="Main Project Area"), 0, wx.ALL, 5)

        text_box = wx.TextCtrl(main_panel, style=wx.TE_MULTILINE)
        main_sizer.Add(text_box, 1, wx.EXPAND | wx.ALL, 5)
        main_panel.SetSizer(main_sizer)

        self._mgr.AddPane(
            main_panel,
            aui.AuiPaneInfo()
            .CenterPane()          # main central area
            .Caption("Workspace")
        )

        # Apply layout
        self._mgr.Update()
        self.Centre()
        self.Show()

class App(wx.App):
    def OnInit(self):
        MainFrame()
        return True

if __name__ == "__main__":
    App(False).MainLoop()
