"""
This source file is part of Web Weaver
For the latest info, see https://github.com/SwatKat1977/WebWeaver

Copyright 2025-2026 SwatKat1977

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.
"""
from pathlib import Path

import wx
from webweaver.studio.studio_solution import StudioSolution
from webweaver.studio.ui.framework.settings_page import SettingsPage, ValidationResult


SCREENSHOT_POLICY_LABELS = {
    "off": "Off",
    "on_failure": "On Failure",
    "all_steps": "All Steps"
}

LABEL_TO_SCREENSHOT_POLICY = {v: k for k, v in SCREENSHOT_POLICY_LABELS.items()}


class GeneralSettingsPage(SettingsPage):
    """Settings page for configuring general solution options.

    This page allows viewing and editing of core solution settings,
    including the solution name (read-only), base URL, and browser
    launch behavior.
    """

    def __init__(self, parent, context: StudioSolution):
        """Initialise the GeneralSettingsPage UI.

        Args:
            parent: The parent wx window.
            context (StudioSolution): The solution context providing
                current values and receiving updates.
        """
        super().__init__(parent)
        self._context: StudioSolution = context

        outer = wx.BoxSizer(wx.VERTICAL)

        # ---- Content container with consistent margins ----
        content = wx.BoxSizer(wx.VERTICAL)

        # ===== General section =====
        self.add_section_title(self, "General", content)

        # --- Solution Name ---
        label = wx.StaticText(self,
                              label="Solution Name")
        font = label.GetFont()
        font = font.Bold()
        label.SetFont(font)
        content.Add(label, 0, wx.BOTTOM, 6)

        self._solution_name = wx.TextCtrl(self, style=wx.TE_READONLY)
        content.Add(self._solution_name, 0, wx.EXPAND | wx.BOTTOM, 12)

        # --- Base URL ---
        label = wx.StaticText(self,
                              label="Base URL")
        font = label.GetFont()
        font = font.Bold()
        label.SetFont(font)
        content.Add(label, 0, wx.BOTTOM, 6)

        self._base_url = wx.TextCtrl(self)
        content.Add(self._base_url, 0, wx.EXPAND | wx.BOTTOM, 12)

        # ---- Launch browser automatically section ----
        self._browser_automatic_checkbox = wx.CheckBox(
            self,
            label="Launch Browser Automatically")
        content.Add(self._browser_automatic_checkbox, 0, wx.BOTTOM, 10)

        # ---- Screenshot policy section ----
        screeshot_label = wx.StaticText(self,
                                        label="Default screenshot policy")
        font = label.GetFont()
        font = font.Bold()
        screeshot_label.SetFont(font)
        content.Add(screeshot_label, 0, wx.BOTTOM, 6)

        self._screenshot_policy = wx.Choice(self)
        for policy, label in SCREENSHOT_POLICY_LABELS.items():
            self._screenshot_policy.Append(label, clientData=policy)
        content.Add(self._screenshot_policy, 0, wx.EXPAND | wx.BOTTOM, 12)

        # --- Screenshots Directory Section ---
        label = wx.StaticText(self,
                              label="Screenshots Directory")
        font = label.GetFont()
        font = font.Bold()
        label.SetFont(font)
        content.Add(label, 0, wx.BOTTOM, 6)

        self._screenshots_dir = wx.DirPickerCtrl(
            self, message="Select code generator directory")
        content.Add(self._screenshots_dir, 0, wx.EXPAND)

        # Add content with clean outer padding
        outer.Add(content, 0, wx.ALL | wx.EXPAND, 20)

        # Push everything upward
        outer.AddStretchSpacer()

        self.SetSizer(outer)

    def load(self):
        """Load values from the solution context into the UI controls."""
        self._solution_name.SetValue(self._context.solution_name)
        self._base_url.SetValue(self._context.base_url)
        self._browser_automatic_checkbox.SetValue(
            self._context.launch_browser_automatically)

        choices = list(SCREENSHOT_POLICY_LABELS.values())
        current_policy = self._context.default_screenshots_policy
        label = SCREENSHOT_POLICY_LABELS[current_policy]
        index = choices.index(label)
        self._screenshot_policy.SetSelection(index)

        screenshots_dir = Path(self._context.screenshots_directory).absolute()
        self._screenshots_dir.SetPath(str(screenshots_dir))

    def validate(self) -> ValidationResult:
        """Validate user input on the page.

        Returns:
            ValidationResult: Result indicating whether validation passed.
                If validation fails, includes an error message and the
                control to focus.
        """
        if not self._base_url.GetValue().strip():
            return ValidationResult(
                ok=False,
                message="Base URL is a required field",
                focus=self._base_url)

        screenshots_dir = Path(self._screenshots_dir.GetPath()).absolute()

        if not screenshots_dir.is_dir():
            return ValidationResult(
                ok=False,
                message="Screenshots directory isn't a valid directory",
                focus=self._screenshots_dir)

        return ValidationResult(True)

    def apply(self):
        """Apply the current UI values to the solution context."""
        self._context.base_url = self._base_url.GetValue().strip()
        self._context.launch_browser_automatically = \
            self._browser_automatic_checkbox.GetValue()

        selection_index = self._screenshot_policy.GetSelection()
        policy = self._screenshot_policy.GetClientData(selection_index)
        self._context.default_screenshots_policy = policy

        self._context.screenshots_directory = str(self._screenshots_dir.GetPath())
