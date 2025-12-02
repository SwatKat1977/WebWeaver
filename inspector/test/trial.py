import wx
import wx.aui as aui

class MainFrame(wx.Frame):
    def __init__(self):
        super().__init__(None, title="Webweaver Automation Studio", size=(1400, 900))

        toolbar_id_new_project: int = 1
        toolbar_id_open_project: int = 2
        toolbar_id_save_project: int = 3
        toolbar_id_inspector_mode: int = 4

        # AUI Manager
        self._mgr = aui.AuiManager(self)

        # =============================
        # 1. TOOLBAR (top, dockable)
        # =============================
        toolbar = aui.AuiToolBar(
            self,
            -1,
            wx.DefaultPosition,
            wx.DefaultSize,
            style=wx.NO_BORDER
                  | aui.AUI_TB_DEFAULT_STYLE
                  | aui.AUI_TB_TEXT
                  | aui.AUI_TB_HORZ_LAYOUT
        )
        toolbar.SetToolBitmapSize((32, 32))
        toolbar.SetToolPacking(5)
        toolbar.SetToolSeparation(5)

        # Add some standard tools
        toolbar.AddTool(toolbar_id_new_project,
                        "",
                        wx.ArtProvider.GetBitmap(wx.ART_NEW,
                                                 wx.ART_TOOLBAR,
                                                 (16,16)),
                        short_help_string="New Project")
        toolbar.AddTool(toolbar_id_open_project,
                        "",
                        wx.ArtProvider.GetBitmap(wx.ART_FILE_OPEN,
                                                 wx.ART_TOOLBAR,
                                                 (16,16)),
                        short_help_string="Open Project")
        toolbar.AddTool(toolbar_id_save_project,
                        "",
                        wx.ArtProvider.GetBitmap(wx.ART_FILE_SAVE,
                                                 wx.ART_TOOLBAR,
                                                 (16,16)),
                        short_help_string="Save Project")

        toolbar.AddSeparator()

        toolbar.AddTool(toolbar_id_inspector_mode,
                        "",
                        wx.ArtProvider.GetBitmap(wx.ART_FIND,
                                                 wx.ART_TOOLBAR,
                                                 (16, 16)),
                        short_help_string="Inspector Mode")

        self.record_icon = wx.ArtProvider.GetBitmap(wx.ART_ERROR,
                                                    wx.ART_TOOLBAR,
                                                    (24, 24))  # red circle
        self.stop_icon = wx.ArtProvider.GetBitmap(wx.ART_CROSS_MARK,
                                                  wx.ART_TOOLBAR,
                                                  (24, 24))  # stop square
        self.record_tool_id = 100

        toolbar.AddTool(self.record_tool_id,
                        "",
                        self.record_icon,
                        short_help_string="Record",
                        kind=wx.ITEM_CHECK)

        toolbar.AddTool(5,
                        "",
                        wx.ArtProvider.GetBitmap(wx.ART_GO_FORWARD,
                                                 wx.ART_TOOLBAR,
                                                 (16,16)))

        toolbar.Realize()

        # --- Bind toggle event ---
        self.Bind(wx.EVT_TOOL, self.__on_record_toggle, id=self.record_tool_id)

        self._mgr.AddPane(
            toolbar,
            aui.AuiPaneInfo()
            .Name("MainToolbar")
            .ToolbarPane()
            .Top()
            .Row(0)
            .Position(0)
            .LeftDockable(False)
            .RightDockable(False)
            .BottomDockable(False)
            .Gripper(False)
            .Floatable(False)
            .Movable(False)
        )

        # -------------------------
        # Projects panel (left top)
        # -------------------------
        project_panel = wx.Panel(self)
        project_sizer = wx.BoxSizer(wx.VERTICAL)
        project_sizer.Add(wx.StaticText(project_panel, label="Projects"), 0, wx.ALL, 5)

        project_tree = wx.TreeCtrl(project_panel, style=wx.TR_HAS_BUTTONS)
        project_sizer.Add(project_tree, 1, wx.EXPAND | wx.ALL, 5)

        # --- IMAGE LIST ---
        image_list = wx.ImageList(16, 16)
        folder_icon = image_list.Add(wx.ArtProvider.GetBitmap(wx.ART_FOLDER, wx.ART_OTHER, (16, 16)))
        file_icon = image_list.Add(wx.ArtProvider.GetBitmap(wx.ART_NORMAL_FILE, wx.ART_OTHER, (16, 16)))
        project_tree.AssignImageList(image_list)

        # --- POPULATE THE TREE ---
        root = project_tree.AddRoot("Solution WebWeaver", image=folder_icon)
        solution_items = project_tree.AppendItem(root, "Solution Items", image=folder_icon)
        android_lib = project_tree.AppendItem(root, "AndroidWebLibrary", image=folder_icon)
        crossplatform = project_tree.AppendItem(root, "CrossPlatform", image=folder_icon)

        project_tree.AppendItem(crossplatform, "References", image=folder_icon)
        project_tree.AppendItem(crossplatform, "Reports", image=folder_icon)
        project_tree.AppendItem(crossplatform, "Instructions", image=folder_icon)

        project_tree.AppendItem(crossplatform, "app.config", image=file_icon)
        project_tree.AppendItem(crossplatform, "CrossPlatform.rxtmg", image=file_icon)
        project_tree.AppendItem(crossplatform, "CrossPlatform.rxtst", image=file_icon)
        project_tree.AppendItem(crossplatform, "CrossPlatformRepository.rxrep", image=file_icon)

        project_tree.ExpandAll()

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

    def __on_record_toggle(self, event):
        toolbar = self._mgr.GetPane("MainToolbar").window
        is_recording = toolbar.GetToolToggled(self.record_tool_id)

        if is_recording:
            toolbar.SetToolBitmap(self.record_tool_id, self.stop_icon)
            toolbar.SetToolShortHelp(self.record_tool_id, "Stop Recording")
        else:
            toolbar.SetToolBitmap(self.record_tool_id, self.record_icon)
            toolbar.SetToolShortHelp(self.record_tool_id, "Start Recording")

        toolbar.Realize()


class App(wx.App):
    def OnInit(self):
        MainFrame()
        return True

if __name__ == "__main__":
    App(False).MainLoop()
