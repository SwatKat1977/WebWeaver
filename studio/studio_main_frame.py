import wx
import wx.aui as aui


class StudioMainFrame(wx.Frame):
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

        # Apply layout
        self._mgr.Update()
        self.Centre()
        self.Show()

    def __on_record_toggle(self, _event):
        toolbar = self._mgr.GetPane("MainToolbar").window
        is_recording = toolbar.GetToolToggled(self.record_tool_id)

        if is_recording:
            toolbar.SetToolBitmap(self.record_tool_id, self.stop_icon)
            toolbar.SetToolShortHelp(self.record_tool_id, "Stop Recording")
        else:
            toolbar.SetToolBitmap(self.record_tool_id, self.record_icon)
            toolbar.SetToolShortHelp(self.record_tool_id, "Start Recording")

        toolbar.Realize()
