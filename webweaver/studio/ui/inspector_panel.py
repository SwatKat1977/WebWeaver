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


class InspectorPanel(wx.Panel):
    """
    Panel that displays information about elements picked in the browser inspector.

    The InspectorPanel acts as a simple log/output view for the live element
    inspector. Whenever the user picks or hovers an element in the browser,
    structured information about that element (tag, id, classes, selectors, etc.)
    can be appended to this panel for debugging, inspection, or future recording
    purposes.

    Currently, the UI consists of a single read-only, multi-line text control
    that shows a chronological log of picked elements.
    """
    # pylint: disable=too-few-public-methods

    def __init__(self, parent: wx.Window):
        """
        Create the inspector panel.

        This constructs the UI and sets up a vertical layout containing a
        read-only multi-line text control used as the inspector log.

        :param parent: Parent wx window that owns this panel.
        """
        super().__init__(parent)

        # Vertical layout: buttons at top, log below
        main_sizer: wx.BoxSizer = wx.BoxSizer(wx.VERTICAL)

        # --- Log area (multiline text) ---
        self._log: wx.TextCtrl = wx.TextCtrl(
            self, wx.ID_ANY, "", style=wx.TE_MULTILINE | wx.TE_READONLY)

        main_sizer.Add(self._log,
                       1,
                       wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM,
                       5)

        self.SetSizer(main_sizer)

    def append_element(self, el: dict):
        """
        Append a picked element description to the inspector log.

        The element is expected to be provided as a dictionary containing
        fields such as:

            - tag
            - id
            - class
            - text
            - css
            - xpath

        Any missing keys are displayed as None.

        :param el: Dictionary describing the picked DOM element.
        """
        self._log.AppendText(
            f"Picked element:\n"
            f"  tag: {el.get('tag')}\n"
            f"  id: {el.get('id')}\n"
            f"  class: {el.get('class')}\n"
            f"  text: {el.get('text')}\n"
            f"  css: {el.get('css')}\n"
            f"  xpath: {el.get('xpath')}\n\n")
