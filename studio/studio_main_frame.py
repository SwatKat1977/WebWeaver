import sys
from typing import Optional
import wx
from solution_explorer_panel import SolutionExplorerPanel

# macOS menu bar offset
INITIAL_POSITION = wx.Point(0, 30) if sys.platform == "darwin" \
    else wx.DefaultPosition

class StudioMainFrame(wx.Frame):
    def __init__(self, parent: Optional[wx.Window] = None):
        super().__init__(
            parent,
            title="Webweaver Automation Studio",
            pos=INITIAL_POSITION,
            size=wx.Size(1024, 768),
            style=wx.DEFAULT_FRAME_STYLE,
        )

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
        ...
