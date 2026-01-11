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
from pathlib import Path
import sys
import typing
import wx
from solution_create_wizard.solution_create_wizard_data \
    import SolutionCreateWizardData
from solution_create_wizard.solution_creation_page import SolutionCreationPage
from solution_create_wizard.solution_wizard_base import SolutionWizardBase


def is_directory_writable(path: Path) -> bool:
    """
    Check whether a directory exists and is writable.
    """
    try:
        path.mkdir(parents=True, exist_ok=True)
        test_file = path / ".write_test"
        with open(test_file, "w") as f:
            f.write("test")
        test_file.unlink()
        return True
    except Exception:
        return False


class WizardBasicInfoPage(SolutionWizardBase):
    # pylint: disable=too-few-public-methods

    MIN_SOLUTION_NAME_LENGTH: int = 60

    NEXT_WIZARD_PAGE = SolutionCreationPage.PAGE_NO_SELECT_BROWSER_PAGE

    ALLOWED_SOLUTION_NAME_CHARS = set(
        "abcdefghijklmnopqrstuvwxyz"
        "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        "0123456789"
        " _-")

    def __init__(self,
                 parent: wx.Window,
                 data: SolutionCreateWizardData,
                 steps: list):
        super().__init__("Create your new solution",
                         parent, data, 0)

        self._txt_solution_name: typing.Optional[wx.TextCtrl] = None
        self._txt_solution_dir: typing.Optional[wx.TextCtrl] = None
        self._chk_create_solution_dir: typing.Optional[wx.CheckBox] = None

        # Header
        self._create_header("Create your new solution",
                            "Define basic information for your first solution.")

        # --------------------------------------------------------------
        # Input Area
        # --------------------------------------------------------------

        input_area_panel: wx.Panel = wx.Panel(self)
        input_area_sizer: wx.FlexGridSizer = wx.FlexGridSizer(0, 3, 8, 8)
        input_area_sizer.AddGrowableCol(1, 1)

        # -----
        # Row 1 : Solution name
        # -----
        input_area_sizer.Add(wx.StaticText(input_area_panel,
                                           wx.ID_ANY,
                                           "Solution name:"),
                             0,
                             wx.ALIGN_CENTER_VERTICAL)
        self._txt_solution_name = wx.TextCtrl(input_area_panel, wx.ID_ANY)
        input_area_sizer.Add(self._txt_solution_name, 1, wx.EXPAND)
        input_area_sizer.AddSpacer(0)
        self._txt_solution_name.SetMaxLength(self.MIN_SOLUTION_NAME_LENGTH)

        # Add validator to solution name input -- only allow letters, spaces,
        # underscores, and hyphens.
        self._txt_solution_name.Bind(wx.EVT_TEXT,
                                     self._on_solution_name_changed)

        # -----
        # Row 2 : Solution location
        # -----
        input_area_sizer.Add(wx.StaticText(input_area_panel,
                                           wx.ID_ANY,
                                           "Location:"),
                                           0, wx.ALIGN_CENTER_VERTICAL)
        self._txt_solution_dir = wx.TextCtrl(input_area_panel, wx.ID_ANY)
        input_area_sizer.Add(self._txt_solution_dir, 1, wx.EXPAND)

        btn_browse_location: wx.Button = wx.Button(input_area_panel,
                                                   wx.ID_ANY,
                                                   "…")
        btn_browse_location.SetMinSize(wx.Size(32, -1))
        btn_browse_location.Bind(wx.EVT_BUTTON,
                                 self._on_browse_solution_location)
        input_area_sizer.Add(btn_browse_location, 0)

        input_area_panel.SetSizer(input_area_sizer)
        self._main_sizer.Add(input_area_panel, 0, wx.EXPAND | wx.ALL, 10)

        # -----
        # Row 3 : Create solution directory checkbox
        # -----
        self._chk_create_solution_dir = wx.CheckBox(
            self, wx.ID_ANY, "Create directory for solution")
        self._chk_create_solution_dir.SetValue(True)
        self._main_sizer.Add(self._chk_create_solution_dir,
                             0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)

        # -----
        # Row 4 : Button bar
        # -----
        self._create_buttons_bar(self._on_next_click, back_button=False)

        self.SetSizerAndFit(self._main_sizer)
        self.CentreOnParent()

    def _on_solution_name_changed(self, event):
        ctrl = self._txt_solution_name
        value = ctrl.GetValue()

        filtered = "".join(c for c in value if c in \
                           self.ALLOWED_SOLUTION_NAME_CHARS)

        if filtered != value:
            pos = ctrl.GetInsertionPoint()
            ctrl.ChangeValue(filtered)
            ctrl.SetInsertionPoint(min(pos - 1, len(filtered)))

        event.Skip()

    def _on_browse_solution_location(self, _event: wx.CommandEvent) -> None:
        dlg = wx.DirDialog(self, "Choose solution location")
        if dlg.ShowModal() == wx.ID_OK:
            self._txtSolutionDir.SetValue(dlg.GetPath())

    def _on_next_click(self, _event):
        if not self._validate_fields():
            return

        self.EndModal(wx.ID_OK)

    def _validate_fields(self) -> bool:
        solution_name = self._txt_solution_name.GetValue().strip()

        if not solution_name:
            wx.MessageBox("Please enter a solution name.", "Validation error", wx.ICON_WARNING)
            return False

        if not self._txt_solution_name.Validate():
            wx.MessageBox(
                "Only letters, spaces, underscores and hyphens are allowed.",
                "Invalid input",
                wx.ICON_WARNING | wx.OK,
                self
            )
            self._txt_solution_name.SetFocus()
            return False

        solution_dir = self._txt_solution_dir.GetValue().strip()

        if not solution_dir:
            wx.MessageBox("Please enter a solution location.",
                          "Validation error", wx.ICON_WARNING)
            return False

        path = Path(solution_dir)

        # Windows root drive protection (C:\)
        if sys.platform == "win32":
            try:
                p = path.resolve()
                if str(p).upper() in ("C:\\", "C:"):
                    wx.MessageBox(
                        "The root of the C: drive is not writable.\n"
                        "Please choose a folder inside your Documents or AppData directory.",
                        "Permission error",
                        wx.ICON_WARNING
                    )
                    return False
            except Exception:
                pass

        if not is_directory_writable(path):
            wx.MessageBox(
                "The specified solution location is not valid or writable.\n"
                "Please choose another location.",
                "Validation error",
                wx.ICON_WARNING
            )
            return False

        # Write back to data object
        self._data.solution_name = solution_name
        self._data.solution_directory = str(path)
        self._data.create_solution_dir = self._chk_create_solution_dir.GetValue()

        return True
