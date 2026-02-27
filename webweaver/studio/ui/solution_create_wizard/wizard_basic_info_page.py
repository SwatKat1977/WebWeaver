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
import os
from pathlib import Path
import sys
import typing
import wx
from webweaver.studio.ui.solution_create_wizard.solution_create_wizard_data \
    import SolutionCreateWizardData
from webweaver.studio.ui.solution_create_wizard.solution_creation_page \
    import SolutionCreationPage
from webweaver.studio.ui.solution_create_wizard.solution_wizard_base import \
    SolutionWizardBase


def is_directory_writable(path: Path) -> bool:
    """
    Check whether an existing directory is writable.
    Does NOT create the directory.
    """
    if not path.exists() or not path.is_dir():
        return False

    try:
        test_file = path / ".ww_write_test_tmp"
        with open(test_file, "w"):
            pass
        test_file.unlink()
        return True
    except OSError:
        return False


class WizardBasicInfoPage(SolutionWizardBase):
    """
    Create the "Basic Information" page of the solution creation wizard.

    This page allows the user to:
      - Enter a solution name (with character validation)
      - Choose a target directory for the solution
      - Optionally create a subdirectory for the solution

    The page validates all user input before allowing the wizard to proceed
    and writes the collected values back into the shared
    SolutionCreateWizardData object upon successful validation.

    Args:
        parent (wx.Window): The parent window that owns this wizard page.
        data (SolutionCreateWizardData): Shared wizard data object used to
            store and retrieve information collected throughout the wizard.
    """
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
                 data: SolutionCreateWizardData):
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
        """
        Handle changes to the solution name text field.

        Filters the input in real time to allow only characters defined in
        ALLOWED_SOLUTION_NAME_CHARS. Any invalid characters are removed
        automatically while preserving the cursor position.
        """
        ctrl = self._txt_solution_name
        value = ctrl.GetValue()

        filtered = "".join(c for c in value if c in \
                           self.ALLOWED_SOLUTION_NAME_CHARS)

        if filtered != value:
            pos = ctrl.GetInsertionPoint()
            ctrl.ChangeValue(filtered)
            new_pos = max(0, min(pos - 1, len(filtered)))
            ctrl.SetInsertionPoint(new_pos)

        event.Skip()

    def _on_browse_solution_location(self, _event: wx.CommandEvent) -> None:
        """
        Open a directory selection dialog for choosing the solution location.

        If the user selects a directory and confirms the dialog, the selected
        path is written into the solution location text field.
        """
        dlg = wx.DirDialog(self, "Choose solution location")
        if dlg.ShowModal() == wx.ID_OK:
            self._txt_solution_dir.SetValue(dlg.GetPath())

    def _on_next_click(self, _event):
        """
        Handle the Next button click event.

        Validates all input fields and, if validation succeeds, closes the
        wizard page and signals successful completion.
        """
        if not self._validate_fields():
            return

        self.EndModal(wx.ID_OK)

    def _validate_fields(self) -> bool:
        """
        Validate all user input fields on the page.

        This method checks:
          - That a solution name is provided and contains only allowed
            characters
          - That a solution directory is provided
          - That the target directory is valid and writable
          - That the root of the C: drive is not used on Windows

        If validation succeeds, the collected values are written back into the
        shared SolutionCreateWizardData object.

        Returns:
            bool: True if all fields are valid, False otherwise.
        """
        solution_name = self._txt_solution_name.GetValue().strip()

        if not solution_name:
            wx.MessageBox("Please enter a solution name.", "Validation error",
                          wx.ICON_WARNING)
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

        if not path.is_absolute():
            wx.MessageBox(
                "Please enter a full directory path or use the Browse button.",
                "Validation error",
                wx.ICON_WARNING
            )
            return False

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
            except OSError:
                pass

        if not is_directory_writable(path):
            wx.MessageBox(
                "The specified solution location is not valid or writable.\n"
                "Please choose another location.",
                "Validation error",
                wx.ICON_WARNING
            )
            return False

        create_solution_dir = self._chk_create_solution_dir.GetValue()

        if create_solution_dir:
            final_path = path / solution_name

            if final_path.exists():
                wx.MessageBox(
                    f"A directory named '{solution_name}' already exists in the selected location.",
                    "Validation error",
                    wx.ICON_WARNING
                )
                return False

        else:
            wws_files = list(path.glob("*.wws"))

            if wws_files:
                wx.MessageBox(
                    "This directory already contains a WebWeaver solution file (.wws).\n"
                    "Please choose a different location.",
                    "Validation error",
                    wx.ICON_WARNING
                )
                return False

        # Write back to data object
        self._data.solution_name = solution_name
        self._data.solution_directory = str(path)
        self._data.create_solution_dir = self._chk_create_solution_dir.GetValue()

        return True
