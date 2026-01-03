import sys
from typing import Optional
import wx
import wx.aui
from solution_explorer_panel import SolutionExplorerPanel
from toolbar_icons import (
    load_toolbar_inspect_icon,
    load_toolbar_new_project_icon,
    load_toolbar_open_project_icon,
    load_toolbar_pause_record_icon,
    load_toolbar_save_project_icon,
    load_toolbar_start_record_icon,
    load_toolbar_stop_record_icon,
    load_toolbar_resume_record_icon,
    load_toolbar_close_solution_icon)

# macOS menu bar offset
INITIAL_POSITION = wx.Point(0, 30) if sys.platform == "darwin" \
    else wx.DefaultPosition

class StudioMainFrame(wx.Frame):

    TOOLBAR_ID_NEW_SOLUTION: int = wx.ID_HIGHEST + 1
    TOOLBAR_ID_OPEN_SOLUTION: int = wx.ID_HIGHEST + 2
    TOOLBAR_ID_SAVE_SOLUTION: int = wx.ID_HIGHEST + 3
    TOOLBAR_ID_CLOSE_SOLUTION: int = wx.ID_HIGHEST + 4
    TOOLBAR_ID_INSPECTOR_MODE: int = wx.ID_HIGHEST + 5
    TOOLBAR_ID_START_STOP_RECORD: int = wx.ID_HIGHEST + 6
    TOOLBAR_ID_PAUSE_RECORD: int = wx.ID_HIGHEST + 7

    def __init__(self, parent: Optional[wx.Window] = None):
        super().__init__(
            parent,
            title="Webweaver Automation Studio",
            pos=INITIAL_POSITION,
            size=wx.Size(1024, 768),
            style=wx.DEFAULT_FRAME_STYLE,
        )

        self._toolbar = None

        self._aui_mgr: wx.aui.AuiManager = wx.aui.AuiManager()

        if sys.platform == "darwin":
            self.EnableFullScreenView(False)

        # --------------------------------------------------------------
        # Menu Bar
        # --------------------------------------------------------------
        menubar = wx.MenuBar()

        # -- File Menu --
        file_menu = wx.Menu()
        file_menu.Append(wx.ID_NEW, "New Project\tCtrl+N")
        file_menu.Append(wx.ID_OPEN, "Open Project\tCtrl+O")

        self._recent_solutions_menu = wx.Menu()
        file_menu.AppendSubMenu(self._recent_solutions_menu,
                                "Recent Solutions")

        file_menu.Append(wx.ID_SAVE, "Save Project\tCtrl+S")
        file_menu.AppendSeparator()
        file_menu.Append(wx.ID_EXIT, "Exit\tCtrl-X")
        menubar.Append(file_menu, "File")
        self.SetMenuBar(menubar)

        # Help menu (actual help items only)
        help_menu = wx.Menu()
        help_menu.Append(wx.ID_ANY, "WebWeaver Help")
        help_menu.Append(wx.ID_ABOUT, "About WebWeaver")
        menubar.Append(help_menu, "Help")

        self.SetMenuBar(menubar)

    def init_aui(self) -> None:
        self._aui_mgr.SetManagedWindow(self)

        # Reset any previously stored layout
        self._aui_mgr.LoadPerspective("", True)

        self._aui_mgr.GetArtProvider().SetMetric(wx.aui.AUI_DOCKART_SASH_SIZE,
                                                2)

        # --------------------------------------------------------------
        # TOOLBAR (top, dockable)
        # --------------------------------------------------------------
        self.create_main_toolbar()

    def create_main_toolbar(self):
        self._toolbar = wx.aui.AuiToolBar(
            self,
            wx.ID_ANY,
            wx.DefaultPosition,
            wx.DefaultSize,
            wx.NO_BORDER
            | wx.aui.AUI_TB_DEFAULT_STYLE
            | wx.aui.AUI_TB_TEXT
            | wx.aui.AUI_TB_HORZ_LAYOUT)

        self._toolbar.SetToolBitmapSize(wx.Size(32, 32))
        self._toolbar.SetToolPacking(5)
        self._toolbar.SetToolSeparation(5)

        self._toolbar.AddTool(
            self.TOOLBAR_ID_NEW_SOLUTION,
            "",
            load_toolbar_new_project_icon(),
            "Create New Solution",)

        self._toolbar.AddTool(
            self.TOOLBAR_ID_OPEN_SOLUTION,
            "",
            load_toolbar_open_project_icon(),
            "Open Solution")

        self._toolbar.AddTool(
            self.TOOLBAR_ID_SAVE_SOLUTION,
            "",
            load_toolbar_save_project_icon(),
            "Save Solution")

        self._toolbar.AddTool(
            self.TOOLBAR_ID_CLOSE_SOLUTION,
            "",
            load_toolbar_close_solution_icon(),
            "Close Solution")

        self._toolbar.AddSeparator()

        self._toolbar.AddTool(
            self.TOOLBAR_ID_INSPECTOR_MODE,
            "",
            load_toolbar_inspect_icon(),
            "Inspector Mode",
            wx.ITEM_CHECK)

        self._toolbar.AddTool(
            self.TOOLBAR_ID_START_STOP_RECORD,
            "",
            load_toolbar_start_record_icon(),
            "Record")

        self._toolbar.AddTool(
            self.TOOLBAR_ID_PAUSE_RECORD,
            "",
            load_toolbar_pause_record_icon(),
            "Pause Recording")

        self._toolbar.Realize()

        '''
        // --- Bind toolbar events ---
        self._toolbar->Bind(wxEVT_TOOL,
            &StudioMainFrame::OnNewSolutionEvent,
            this,
            TOOLBAR_ID_NEW_SOLUTION);

        self._toolbar->Bind(wxEVT_TOOL,
            &StudioMainFrame::OnCloseSolutionEvent,
            this,
            TOOLBAR_ID_CLOSE_SOLUTION);

        self._toolbar->Bind(wxEVT_TOOL,
            &StudioMainFrame::OnOpenSolutionEvent,
            this,
            TOOLBAR_ID_OPEN_SOLUTION);

        self._toolbar->Bind(wxEVT_TOOL,
            &StudioMainFrame::OnRecordStartStopEvent,
            this,
            TOOLBAR_ID_START_STOP_RECORD);

        self._toolbar->Bind(wxEVT_TOOL,
            &StudioMainFrame::OnRecordPauseEvent,
            this,
            TOOLBAR_ID_PAUSE_RECORD);

        self._toolbar->Bind(wxEVT_TOOL,
            &StudioMainFrame::OnInspectorEvent,
            this,
            TOOLBAR_ID_INSPECTOR_MODE);
        '''

        self._aui_mgr.AddPane(
            self._toolbar,
            wx.aui.AuiPaneInfo()
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
            .Movable(False))

        self._aui_mgr.Update()
