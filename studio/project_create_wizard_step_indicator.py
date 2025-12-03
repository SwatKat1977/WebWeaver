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


class WizardStepIndicator(wx.Panel):
    """
    A horizontal step indicator widget for wizard dialogs.

    This control displays a series of labeled steps such as:
        ● Basic data     ○ Web application     ○ Configure     ○ Finish

    The active step is shown with a filled circle (●), while inactive
    steps use an open circle (○). Calling `set_active(index)` updates the
    indicator and highlights the current step.

    Parameters
    ----------
    parent : wx.Window
        The parent window.
    steps : list[str]
        A list of step names to display.
    active_index : int, optional
        The index of the initially active step (default is 0).
    """

    def __init__(self, parent, steps, active_index=0):
        super().__init__(parent)
        self.steps = steps
        self.labels = []
        self._active_index = -1

        sizer = wx.BoxSizer(wx.HORIZONTAL)

        for _ in enumerate(steps):
            label = wx.StaticText(self, label="")
            sizer.Add(label, 0, wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 20)
            self.labels.append(label)

        self.SetSizer(sizer)
        self.__set_active(active_index)

    def __set_active(self, index: int):
        """
        Update the indicator to highlight the active step.

        Parameters
        ----------
        index : int
            The index of the step to mark as active.

        Notes
        -----
        - The active step shows a filled circle (●).
        - Inactive steps show an open circle (○).
        - Colours are updated to visually distinguish the active step.
        """
        self._active_index = index
        for idx, label in enumerate(self.labels):
            bullet = u"\u25CF" if idx == index else u"\u25CB"  # ● or ○

            label.SetLabel(f"{bullet} {self.steps[idx]}")
            if idx == index:
                label.SetForegroundColour(wx.Colour(0, 0, 0))
            else:
                label.SetForegroundColour(wx.Colour(130, 130, 130))
