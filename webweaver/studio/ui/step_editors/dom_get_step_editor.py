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


class DomGetStepEditor(wx.Dialog):
    """
    Dialog for creating or editing a DOM_GET playback step.

    This editor allows the user to configure a data extraction step that:

    - Locates a DOM element via XPath
    - Reads a selected property from that element
      (e.g. text, value, checked state, inner HTML)
    - Stores the extracted value into a named playback variable

    The provided ``event`` dictionary is modified in place. On confirmation,
    the updated values are written back into ``event["payload"]``.

    Attributes:
        _event (dict):
            The recording event dictionary being edited.
        _index (int):
            The step index within the recording timeline (currently informational).
        changed (bool):
            Indicates whether the dialog resulted in a confirmed modification.
    """
    # pylint: disable=too-few-public-methods

    def __init__(self, parent, index, event: dict):
        """
        Initialise the DOM getter step editor dialog.

        Args:
            parent:
                The parent wxPython window.
            index (int):
                Index of the step being edited in the timeline.
                Included for interface consistency with other step editors.
            event (dict):
                The event dictionary containing a ``payload`` entry
                representing the DOM_GET step configuration.
        """
        super().__init__(parent, title="Edit DOM Getter")

        self._event = event
        self.changed = False
        self._index = index
        self._original_payload = event["payload"].copy()

        main_sizer = wx.BoxSizer(wx.VERTICAL)

        grid = wx.FlexGridSizer(rows=3, cols=2, hgap=10, vgap=10)
        grid.AddGrowableCol(1, 1)  # Make second column expand

        payload = event.get("payload")

        # --- XPath ---
        xpath_label = wx.StaticText(self, label="XPath:")
        self._xpath_ctrl = wx.TextCtrl(
            self,
            value=payload.get("xpath", ""))

        grid.Add(xpath_label, 0, wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self._xpath_ctrl, 1, wx.EXPAND)

        # --- Property Type ---
        property_label = wx.StaticText(self, label="Property Type:")
        self._property_choice = wx.Choice(
            self,
            choices=["text", "value", "checked", "html"])
        current_property = payload.get("property_type", "text")
        self._property_choice.SetStringSelection(current_property)

        grid.Add(property_label, 0, wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self._property_choice, 1, wx.EXPAND)

        # --- Output Variable ---
        variable_label = wx.StaticText(self, label="Output Variable:")
        self._variable_ctrl = wx.TextCtrl(
            self,
            value=payload.get("output_variable", ""))

        grid.Add(variable_label, 0, wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self._variable_ctrl, 1, wx.EXPAND)

        main_sizer.Add(grid, 0, wx.ALL | wx.EXPAND, 20)

        # --- Buttons ---
        button_sizer = self.CreateButtonSizer(wx.OK | wx.CANCEL)
        main_sizer.Add(button_sizer, 0, wx.ALL | wx.ALIGN_RIGHT, 10)

        self.SetSizer(main_sizer)
        self.Fit()

        w, h = self.GetSize()
        self.SetSize((w + 60, h))
        self.SetMinSize((w + 60, h))

        self.Centre()

        self.Bind(wx.EVT_BUTTON, self._on_ok, id=wx.ID_OK)

    def _on_ok(self, _evt):
        """
        Persist the edited values back into the event payload.

        Updates the following payload fields:

        - ``xpath``: XPath expression identifying the target element.
        - ``property_type``: The element property to read during playback.
        - ``output_variable``: Name of the playback context variable in
          which the extracted value will be stored.

        The event dictionary is modified in place. The dialog then closes
        with ``wx.ID_OK``.
        """

        new_xpath = self._xpath_ctrl.GetValue()
        new_property = self._property_choice.GetStringSelection()
        new_output = self._variable_ctrl.GetValue()

        if (new_xpath != self._original_payload.get("xpath") or
                new_property != self._original_payload.get("property_type") or
                new_output != self._original_payload.get("output_variable")):

            # Update payload in place
            self._event["payload"]["xpath"] = self._xpath_ctrl.GetValue()
            self._event["payload"]["property_type"] = self._property_choice.GetStringSelection()
            self._event["payload"]["output_variable"] = self._variable_ctrl.GetValue()

            self.changed = True

        self.EndModal(wx.ID_OK)
