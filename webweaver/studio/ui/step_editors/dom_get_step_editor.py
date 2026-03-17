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
from webweaver.studio.persistence.recording_document import DomGetPayload
from webweaver.studio.ui.fancy_dialog_base import FancyDialogBase


class DomGetStepEditor(FancyDialogBase):
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
        changed (bool):
            Indicates whether the dialog resulted in a confirmed modification.
    """
    # pylint: disable=too-many-instance-attributes

    def __init__(self, parent, event: dict):
        """
        Initialise the DOM getter step editor dialog.

        Args:
            parent:
                The parent wxPython window.
            event (dict):
                The event dictionary containing a ``payload`` entry
                representing the DOM_GET step configuration.
        """
        super().__init__(
            parent,
            "Edit DOM Get Step",
            "Edit DOM Get Step",
            "Configure how the automation performs a DOM Get.")

        self.changed = False
        self._event = event
        self._original_payload = event["payload"].copy()

        payload = DomGetPayload(**event.get("payload", {}))

        # --- Step Label
        self._field_step_label = self.add_field("Step Label:", wx.TextCtrl)
        self._field_step_label.SetValue(payload.label)

        # --- XPath
        self._field_xpath = self.add_field("XPath:", wx.TextCtrl)
        self._field_xpath.SetValue(payload.xpath)

        # --- Property Type
        self._field_property_type = self.add_field(
            "Property Type:",
            lambda parent: wx.Choice(parent,
                                   choices=["text", "value","checked",
                                            "html"]))
        current_property = payload.property_type
        self._field_property_type.SetStringSelection(current_property)

        # --- Output Variable
        self._field_output_variable = self.add_field("Output Variable:",
                                                     wx.TextCtrl)
        self._field_output_variable.SetValue(payload.output_variable)

        self.finalise()

    def _ok_event(self):
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

        new_step_label = self._field_step_label.GetValue()
        new_xpath = self._field_xpath.GetValue()
        new_property = self._field_property_type.GetStringSelection()
        new_output = self._field_output_variable.GetValue()

        if (new_xpath != self._original_payload.get("xpath") or
                new_property != self._original_payload.get("property_type") or
                new_output != self._original_payload.get("output_variable") or
                new_step_label != self._original_payload.get("label")):

            # Update payload in place
            self._event["payload"]["label"] = new_step_label
            self._event["payload"]["xpath"] = new_xpath
            self._event["payload"]["property_type"] = new_property
            self._event["payload"]["output_variable"] = new_output

            self.changed = True

        self.EndModal(wx.ID_OK)
