"""
This source file is part of Web Weaver
For the latest info, see https://github.com/SwatKat1977/WebWeaver

Copyright 2025-2026 Webweaver Development Team

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
import wx


def create_main_menu(frame: "StudioMainFrame") -> None:
    """
    Create and configure the main application menu bar.
    """

    menubar = wx.MenuBar()

    # -- File Menu --
    file_menu = wx.Menu()
    file_menu.Append(wx.ID_NEW, "New Project\tCtrl+N")
    file_menu.Append(wx.ID_OPEN, "Open Project\tCtrl+O")

    frame.recent_solutions_menu = wx.Menu()
    file_menu.AppendSubMenu(frame.recent_solutions_menu,
                            "Recent Solutions")

    file_menu.Append(wx.ID_SAVE, "Save Project\tCtrl+S")
    file_menu.AppendSeparator()
    file_menu.Append(wx.ID_EXIT, "Exit\tCtrl-X")
    menubar.Append(file_menu, "File")

    # Code Generation menu
    code_generation_menu = wx.Menu()
    frame.code_generation_menu = wx.Menu()
    code_generation_menu.AppendSubMenu(
        frame.code_generation_menu,
        "Generate")
    code_generation_menu.AppendSeparator()
    code_generation_refresh_id = code_generation_menu.Append(
        wx.ID_ANY, "Refresh Generators")
    menubar.Append(code_generation_menu, "&Code Generation")

    frame.Bind(wx.EVT_MENU, frame.on_refresh_codegen_generators,
               code_generation_refresh_id)

    # -- Help Menu --
    help_menu = wx.Menu()
    help_menu.Append(wx.ID_ANY, "WebWeaver Help")
    help_menu.Append(wx.ID_ABOUT, "About WebWeaver")
    menubar.Append(help_menu, "Help")

    frame.SetMenuBar(menubar)

    # Load and populate recent solutions
    frame.recent_solutions.load()
    frame.rebuild_recent_solutions_menu()

    # Load and populate the code generation plugins
    frame.rebuild_code_generation_menu()
