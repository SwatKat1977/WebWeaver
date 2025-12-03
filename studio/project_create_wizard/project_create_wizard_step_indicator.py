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


class ProjectCreateWizardStepIndicator(wx.Panel):
    """
    A visual step indicator used in the Project Creation wizard.

    This widget displays a horizontal sequence of steps—each represented
    by a small colored circle and a text label—to indicate progress through
    the wizard. The currently active step is highlighted with a green circle
    and darker text, while inactive steps appear in grey.

    Parameters
    ----------
    parent : wx.Window
        The parent window or panel that this indicator belongs to.
    active_index : int, optional
        The zero-based index of the step that should be shown as active.
        Defaults to 1.

    Notes
    -----
    The indicator currently supports four predefined steps:
    * "Basic data"
    * "Web application"
    * "Configure behavior"
    * "Finish"

    The circles are drawn manually using a paint event handler to allow for
    custom coloring and sizing.
    """
    # pylint: disable=too-few-public-methods

    def __init__(self, parent, active_index=1):
        """
        Initialise the step indicator widget.

        This sets up the layout of step circles and labels, and highlights
        the step specified by ``active_index``.

        Args:
            parent (wx.Window): The parent window or panel.
            active_index (int, optional): Zero-based index of the step to
                highlight as active. Defaults to 1.
        """
        super().__init__(parent)
        steps = ["Basic data", "Web application", "Configure behavior", "Finish"]
        sizer = wx.BoxSizer(wx.HORIZONTAL)

        for i, label in enumerate(steps):
            circle_color = "#4CAF50" if i == active_index else "#CCCCCC"
            text_color = "#000000" if i == active_index else "#999999"

            circle = wx.Panel(self, size=(12, 12))
            circle.SetBackgroundColour(self.GetBackgroundColour())
            circle.Bind(wx.EVT_PAINT,
                        lambda evt, p=circle, c=circle_color: self.draw_circle(evt, p, c))

            sizer.Add(circle, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 6)

            t = wx.StaticText(self, label=label)
            t.SetForegroundColour(text_color)
            sizer.Add(t, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 25)

        self.SetSizer(sizer)

    def draw_circle(self, _evt, panel, color):
        """
        Draws a filled circular indicator inside the given panel.

        This method is bound to each circle panel's paint event and is
        responsible for rendering the colored step indicator. The circle
        automatically scales to fit the panel's dimensions.

        Parameters
        ----------
        _evt : wx.PaintEvent
            The paint event triggered by wxPython.
        panel : wx.Panel
            The panel on which the circle should be drawn.
        color : str or wx.Colour
            The fill color of the circle, typically representing whether the
            step is active or inactive.
        """
        device_context: wx.PaintDC = wx.PaintDC(panel)
        device_context.SetBrush(wx.Brush(color))
        device_context.SetPen(wx.Pen(color))
        width, height = panel.GetSize()
        device_context.DrawCircle(width // 2,
                                  height // 2,
                                  min(width, height) // 2)
