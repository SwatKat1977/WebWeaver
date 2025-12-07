"""
This source file is part of Web Weaver
For the latest info, see https://github.com/SwatKat1977/WebWeaver

Copyright 2025 SwatKat1977

    This program is free software : you can redistribute it and /or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.If not, see < https://www.gnu.org/licenses/>.
"""
import wx
import wx.aui as aui
from project_create_wizard.wizard_ids import ID_BACK_BUTTON
from project_create_wizard.wizard_basic_info_page import WizardBasicInfoPage
from project_create_wizard.wizard_web_select_browser_page import WizardWebSelectBrowserPage
from project_create_wizard.wizard_web_behaviour_page import WizardWebBehaviourPage
from project_create_wizard.wizard_finish_page import WizardFinishPage
from bitmap_utils import BitmapUtils
import toolbar_icons


class StudioMainFrame(wx.Frame):
    def __init__(self):
        super().__init__(None,
                         title="Webweaver Automation Studio",
                         size=(1400, 900),
                         style=wx.DEFAULT_FRAME_STYLE)

        # AUI Manager
        self._mgr = aui.AuiManager(self)

        menubar = wx.MenuBar()
        menu = wx.Menu()
        menu.Append(wx.ID_EXIT, "Quit")
        menubar.Append(menu, "File")
        self.SetMenuBar(menubar)

        # 1. TOOLBAR (top, dockable)
        self.__create_toolbar()

        # 2. Projects panel (left top)
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
        project_tree.AppendItem(root, "Solution Items", image=folder_icon)
        project_tree.AppendItem(root, "AndroidWebLibrary", image=folder_icon)
        crossplatform = project_tree.AppendItem(root, "CrossPlatform", image=folder_icon)

        project_tree.AppendItem(crossplatform, "References", image=folder_icon)
        project_tree.AppendItem(crossplatform, "Reports", image=folder_icon)
        project_tree.AppendItem(crossplatform, "Instructions", image=folder_icon)

        project_tree.AppendItem(crossplatform, "app.config", image=file_icon)
        project_tree.AppendItem(crossplatform, "Sample.wwA", image=file_icon)
        project_tree.AppendItem(crossplatform, "Sample.wwB", image=file_icon)
        project_tree.AppendItem(crossplatform, "Repository.repo", image=file_icon)

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
            .BestSize(300, 300))

        # -------------------------
        # Modules panel (left bottom)
        # -------------------------
        modules_panel = wx.Panel(self)
        modules_sizer = wx.BoxSizer(wx.VERTICAL)
        modules_sizer.Add(wx.StaticText(modules_panel, label="Modules"), 0, wx.ALL, 5)
        modules_tree = wx.TreeCtrl(modules_panel, style=wx.TR_HAS_BUTTONS)
        modules_sizer.Add(modules_tree, 1, wx.EXPAND | wx.ALL, 5)
        modules_panel.SetSizer(modules_sizer)

        # Add below the Projects panel
        self._mgr.AddPane(
            modules_panel,
            aui.AuiPaneInfo()
            .Left()
            .Caption("Modules")
            .CloseButton(True)
            .MaximizeButton(True)
            .MinimizeButton(True)
            .BestSize(300, 300)
            .Position(1))

        # -------------------------
        # Main workspace (center)
        # -------------------------
        main_panel = wx.Panel(self)
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(wx.StaticText(main_panel, label="Main Project Area"), 0, wx.ALL, 5)

        text_box = wx.TextCtrl(main_panel, style=wx.TE_MULTILINE)
        main_sizer.Add(text_box, 1, wx.EXPAND | wx.ALL, 5)
        main_panel.SetSizer(main_sizer)

        # Add main central area
        self._mgr.AddPane(
            main_panel,
            aui.AuiPaneInfo()
            .CenterPane()
            .Caption("Workspace"))

        # Apply layout
        self._mgr.Update()
        self.Centre()
        self.Show()

    def __create_toolbar(self):
        toolbar_id_new_project: int = 1
        toolbar_id_open_project: int = 2
        toolbar_id_save_project: int = 3
        toolbar_id_inspector_mode: int = 4

        toolbar = aui.AuiToolBar(
            self,
            -1,
            wx.DefaultPosition,
            wx.DefaultSize,
            style=wx.NO_BORDER
                  | aui.AUI_TB_DEFAULT_STYLE
                  | aui.AUI_TB_TEXT
                  | aui.AUI_TB_HORZ_LAYOUT)
        toolbar.SetToolBitmapSize((32, 32))
        toolbar.SetToolPacking(5)
        toolbar.SetToolSeparation(5)

        neww_project_icon_bmp = BitmapUtils.bitmap_from_base64(
            toolbar_icons.NEW_PROJECT_BUTTON_ICON)
        # Add some standard tools
        toolbar.AddTool(toolbar_id_new_project,
                        "",
                        neww_project_icon_bmp,
                        short_help_string="New Project")

        open_icon_bmp = BitmapUtils.bitmap_from_base64(
            toolbar_icons.OPEN_BUTTON_ICON)
        toolbar.AddTool(toolbar_id_open_project,
                        "",
                        open_icon_bmp,
                        short_help_string="Open Project")

        toolbar.AddTool(toolbar_id_save_project,
                        "",
                        wx.ArtProvider.GetBitmap(wx.ART_FILE_SAVE,
                                                 wx.ART_TOOLBAR,
                                                 (16,16)),
                        short_help_string="Save Project")

        toolbar.AddSeparator()

        inspect_icon_bmp = BitmapUtils.bitmap_from_base64(
            toolbar_icons.INSPECT_BUTTON_ICON)

        toolbar.AddTool(toolbar_id_inspector_mode,
                        "",
                        inspect_icon_bmp,
                        short_help_string="Inspector Mode")

        self.record_icon_bmp = BitmapUtils.bitmap_from_base64(
            toolbar_icons.RECORD_BUTTON_ICON)

        self.stop_record_icon = BitmapUtils.bitmap_from_base64(
            toolbar_icons.STOP_BUTTON_ICON)

        self.record_tool_id = 100

        pause_icon_bmp = BitmapUtils.bitmap_from_base64(
            toolbar_icons.PAUSE_BUTTON_ICON)

        toolbar.AddTool(self.record_tool_id,
                        "",
                        self.record_icon_bmp,
                        short_help_string="Record",
                        kind=wx.ITEM_CHECK)


        toolbar.AddTool(5,
                        "",
                        pause_icon_bmp)

        toolbar.Realize()

        # --- Bind toolbar events ---
        self.Bind(wx.EVT_TOOL,
                  self.__on_new_project,
                  id=toolbar_id_new_project)
        self.Bind(wx.EVT_TOOL,
                  self.__on_record_toggle,
                  id=self.record_tool_id)

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
            .Movable(False))

    def __on_new_project(self, _event):
        data = {}

        page = 1
        while True:
            if page == 1:
                dlg = WizardBasicInfoPage(self, data)
            elif page == 2:
                dlg = WizardWebSelectBrowserPage(self, data)

            elif page == 3:
                dlg = WizardWebBehaviourPage(self, data)

            elif page == 4:
                dlg = WizardFinishPage(self, data)

            else:
                break

            rc = dlg.ShowModal()

            if rc == wx.ID_CANCEL:
                return  # wizard cancelled

            if rc == ID_BACK_BUTTON:
                page -= 1
                continue

            if rc == wx.ID_OK:
                page += 1
                continue

        print("DATA:", data)

    def __on_record_toggle(self, _event):
        toolbar = self._mgr.GetPane("MainToolbar").window
        is_recording = toolbar.GetToolToggled(self.record_tool_id)

        if is_recording:
            toolbar.SetToolBitmap(self.record_tool_id, self.stop_record_icon)
            toolbar.SetToolShortHelp(self.record_tool_id, "Stop Recording")
        else:
            toolbar.SetToolBitmap(self.record_tool_id, self.record_icon_bmp)
            toolbar.SetToolShortHelp(self.record_tool_id, "Start Recording")

        toolbar.Realize()
