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
import wx


class WizardStepIndicator(wx.Panel):
    """
    A horizontal wizard step indicator control.

    Displays a list of steps with a circular bullet in front of each one.
    The currently active step is shown with a filled circle (●) and black text,
    while inactive steps are shown with a hollow circle (○) and grey text.

    This control is intended to be used at the top of wizard-style dialogs
    to show the user's progress through a multi-step workflow.
    """
    # pylint: disable=too-few-public-methods

    def __init__(self, parent: wx.Window, steps, active_index: int = 0):
        """
        Create a new WizardStepIndicator.

        :param parent: Parent wx window.
        :param steps: Iterable of step names (strings).
        :param active_index: Index of the initially active step.
        """
        super().__init__(parent)

        self._steps: list = list(steps)
        self._labels = []
        self._active_index: int = active_index

        sizer: wx.BoxSizer = wx.BoxSizer(wx.HORIZONTAL)

        for _ in self._steps:
            label: wx.StaticText = wx.StaticText(self, wx.ID_ANY, "")
            sizer.Add(label, 0, wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 20)
            self._labels.append(label)

        self.SetSizer(sizer)
        self.set_active(self._active_index)

    def set_active(self, index: int):
        """
        Set the currently active step.

        The active step will be shown with a filled circle (●) and black text.
        All other steps will be shown with a hollow circle (○) and grey text.

        If the index is out of range, the call is ignored.

        :param index: Index of the step to activate.
        """
        if index < 0 or index >= len(self._steps):
            return

        self._active_index = index

        for i, label in enumerate(self._labels):
            if i == index:
                bullet = "●"  # U+25CF
                label.SetForegroundColour(wx.Colour(0, 0, 0))
            else:
                bullet = "○"  # U+25CB
                label.SetForegroundColour(wx.Colour(130, 130, 130))

            label.SetLabel(f"{bullet} {self._steps[i]}")

        self.Layout()
        self.Refresh()
