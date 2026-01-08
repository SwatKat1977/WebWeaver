"""
This source file is part of Web Weaver
For the latest info, see https://github.com/SwatKat1977/WebWeaver

Copyright 2025 SwatKat1977

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
from wizard_step_indicator import WizardStepIndicator
from project_create_wizard.project_create_wizard_data \
    import ProjectCreateWizardData


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


class WizardBasicInfoPage(wx.Dialog):

    MIN_SOLUTION_NAME_LENGTH: int = 60

    NEXT_WIZARD_PAGE = None

    def __init__(self, parent, data: ProjectCreateWizardData, steps: list):
        super().__init__(parent, title="Create your new solution",
                         style=wx.DEFAULT_DIALOG_STYLE)

        self._data = data
        self._steps: list = list(steps)
        self._allowed_chars = set(
            "abcdefghijklmnopqrstuvwxyz"
            "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
            "0123456789"
            " _-")

        self._txt_solution_name: typing.Optional[wx.TextCtrl] = None
        self._txt_solution_dir: typing.Optional[wx.TextCtrl] = None
        self._chk_create_solution_dir: typing.Optional[wx.CheckBox] = None

        main: wx.BoxSizer = wx.BoxSizer(wx.VERTICAL)

        step_indicator: WizardStepIndicator = WizardStepIndicator(
            self, self._steps, 0)
        main.Add(step_indicator, 0, wx.EXPAND | wx.ALL, 10)

        # --------------------------------------------------------------
        # Header
        # --------------------------------------------------------------
        header: wx.BoxSizer = wx.BoxSizer(wx.HORIZONTAL)
        icon: wx.StaticBitmap = wx.StaticBitmap(
            self,
            wx.ID_ANY,
            wx.ArtProvider.GetBitmap(wx.ART_TIP,
                                     wx.ART_OTHER,
                                     wx.Size(32, 32)))
        header.Add(icon, 0, wx.ALL, 10)

        # Text area (vertical sizer)
        header_area: wx.BoxSizer = wx.BoxSizer(wx.VERTICAL)

        # Title
        title: wx.StaticText = wx.StaticText(
            self,
            wx.ID_ANY,
            "Create your new solution")
        title.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT,
                              wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))

        # Subtitle
        subtitle: wx.StaticText = wx.StaticText(
            self,
            wx.ID_ANY,
            "Define basic information for your first solution.")
        subtitle.SetForegroundColour(wx.Colour(100, 100, 100))
        header_area.Add(title, 0)
        header_area.Add(subtitle, 0, wx.TOP, 4)

        # Add text area into header sizer
        header.Add(header_area, 1, wx.ALIGN_CENTER_VERTICAL)

        # Add the whole header to main sizer
        main.Add(header, 0, wx.LEFT | wx.RIGHT, 10)

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
        main.Add(input_area_panel, 0, wx.EXPAND | wx.ALL, 10)

        # -----
        # Row 3 : Create solution directory checkbox
        # -----
        self._chk_create_solution_dir = wx.CheckBox(
            self, wx.ID_ANY, "Create directory for solution")
        self._chk_create_solution_dir.SetValue(True)
        main.Add(self._chk_create_solution_dir,
                 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)

        # -----
        # Row 4 : Button bar
        # -----
        button_bar_sizer: wx.BoxSizer = wx.BoxSizer(wx.HORIZONTAL)
        # Spacer to push buttons to the right
        button_bar_sizer.AddStretchSpacer()

        # Cancel button
        btn_cancel: wx.Button = wx.Button(self, wx.ID_CANCEL, "Cancel")
        btn_cancel.Bind(wx.EVT_BUTTON, lambda evt: self.EndModal(wx.ID_CANCEL))
        button_bar_sizer.Add(btn_cancel, 0, wx.RIGHT, 10)

        # Next button
        btn_next: wx.Button = wx.Button(self, wx.ID_OK, "Next")
        btn_next.Bind(wx.EVT_BUTTON, self._on_next_click)
        button_bar_sizer.Add(btn_next, 0)

        # Add to main layout
        main.Add(button_bar_sizer, 0, wx.EXPAND | wx.ALL, 10)

        self.SetSizerAndFit(main)
        self.CentreOnParent()

    def _on_solution_name_changed(self, event):
        ctrl = self._txt_solution_name
        value = ctrl.GetValue()

        filtered = "".join(c for c in value if c in self._allowed_chars)

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
