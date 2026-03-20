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


class StepInformationOverlay(wx.PopupTransientWindow):
    """Popup overlay displaying information about a playback step.

    This transient window presents contextual details for a given step in the
    playback timeline, such as click, type, or assert actions. It is designed
    to appear as a lightweight informational tooltip-style overlay.

    Attributes:
        title (wx.StaticText): Label displaying the step type.
        body (wx.StaticText): Label displaying detailed step information.
    """

    def __init__(self, parent):
        """Initializes the StepInformationOverlay.

        Args:
            parent (wx.Window): The parent window for this popup.
        """
        super().__init__(parent)

        panel = wx.Panel(self, style=wx.BORDER_SIMPLE)
        panel.SetBackgroundColour(wx.Colour(255, 255, 240))

        self.title = wx.StaticText(panel, label="")
        self.title.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT,
                                   wx.FONTSTYLE_NORMAL,
                                   wx.FONTWEIGHT_BOLD))

        self.body = wx.StaticText(panel, label="")

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.title, 0, wx.ALL, 8)
        sizer.Add(self.body, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 8)

        panel.SetSizer(sizer)

        main = wx.BoxSizer(wx.VERTICAL)
        main.Add(panel)

        self.SetSizerAndFit(main)

    def update(self, step):
        """Updates the overlay content based on the provided step.

        The displayed title and body content are adjusted depending on the
        step type. Supported step types include "click", "type", and "assert".

        Args:
            step (dict): A dictionary describing the step. Expected keys vary
                by type but may include:
                    - type (str): The step type ("click", "type", "assert").
                    - xpath (str): XPath of the target element.
                    - value (str, optional): Input value for click/type steps.
                    - assert_type (str, optional): Assertion type.
                    - expected (str, optional): Expected value for assertions.
                    - soft (bool, optional): Whether assertion is soft.

        Raises:
            KeyError: If required keys for a given step type are missing.
        """

        if step["type"] == "click":
            self.title.SetLabel("Click")
            self.body.SetLabel(
                f"XPath:\n{step['xpath']}\n\n"
                f"Value:\n{step.get('value','-')}")

        elif step["type"] == "type":
            self.title.SetLabel("Type")
            self.body.SetLabel(
                f"XPath:\n{step['xpath']}\n\n"
                f"Value:\n{step['value']}")

        elif step["type"] == "assert":
            self.title.SetLabel("Assert")
            self.body.SetLabel(
                f"XPath:\n{step['xpath']}\n\n"
                f"Type: {step['assert_type']}\n"
                f"Expected: {step['expected']}\n"
                f"Soft: {step['soft']}")

        self.Layout()
        self.Fit()
