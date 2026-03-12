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
import dataclasses
import wx
from webweaver.studio.persistence.recording_document import SendkeysPayload
from webweaver.studio.ui.step_editors.sendkey_key_selection_dialog \
    import SendkeyKeySelectionDialog
from webweaver.studio.ui.fancy_dialog_base import FancyDialogBase


class SendkeysStepEditor(FancyDialogBase):
    """Dialog used to edit a Send Keys step.

    This dialog allows the user to configure a sequence of keyboard inputs
    that will be sent to a target element during playback. The sequence can
    contain both literal text and special keys (with optional modifiers).

    The user can add text entries, add key presses, remove entries, and
    reorder the sequence before saving.

    Attributes:
        KEY_CHOICES (list[str]): List of available special keys that may be
            inserted into the sequence.
        _event (dict): The event dictionary that will receive the edited
            payload when the dialog is saved.
        _sequence (list[dict]): Ordered list of key definitions representing
            the send-keys sequence.
        changed (bool): Indicates whether the dialog resulted in a change
            that should be persisted.
    """
    # pylint: disable=too-many-instance-attributes, too-few-public-methods

    KEY_CHOICES = [
        "ENTER", "TAB", "ESCAPE", "BACKSPACE", "DELETE",
        "SPACE", "ARROW_UP", "ARROW_DOWN",
        "ARROW_LEFT", "ARROW_RIGHT", "HOME", "END"
    ]

    def __init__(self, parent, index: int, event):
        """Initializes the Send Keys step editor dialog.

        Args:
            parent (wx.Window): Parent window that owns this dialog.
            _index (int): Index of the step being edited. Currently unused
                but retained for interface consistency.
            event (dict, optional): Existing event definition containing a
                payload to populate the dialog with. Defaults to None.
        """
        super().__init__(
            parent,
            "Send Keys Step",
            "Edit Send Keys Step",
            "Configure how the automation sends keystrokes.")

        self._event = event
        self._index = index
        self._sequence = []
        self.changed = False

        payload = SendkeysPayload(**event.get("payload", {}))

        # Step label
        self._field_step_label = self.add_field("Step Label:", wx.TextCtrl)
        self._field_step_label.SetValue(payload.label)

        # Target Element
        self._field_target_element = self.add_field("Target Element:",
                                                    wx.TextCtrl)
        self._field_target_element.SetValue(payload.label)

        # Keystroke Sequence
        # pylint: disable=unnecessary-lambda
        self._field_sequence = self.add_full_width_field(
            "Sequence:",
            lambda parent: wx.ListBox(parent))
        self._field_sequence.SetMinSize((-1, 150))
        self._field_sequence.Bind(wx.EVT_LISTBOX_DCLICK, self._on_edit_item)

        self._sequence = list(payload.keys)
        self._field_target_element.SetValue(payload.target)

        buttons_list = [
            ("Add Text", self._on_add_text),
            ("Add Key", self._on_add_key),
            ("Remove", self._on_remove),
            ("Move Up", self._on_move_up),
            ("Move Down", self._on_move_down),
        ]
        button_ctrls = self.add_centered_buttons(buttons_list)
        self._add_text_btn = button_ctrls[0]
        self._add_key_btn = button_ctrls[1]
        self._remove_btn = button_ctrls[2]
        self._up_btn = button_ctrls[3]
        self._down_btn = button_ctrls[4]
        self._add_key_btn.SetToolTip(
            "Key shortcuts are only available when no target element is "
            "specified.")

        self._field_target_element.Bind(wx.EVT_TEXT,
                                        self._on_target_changed)

        self.finalise()

        self._refresh_list()

        self._on_target_changed(None)

    def format_item(self, item: dict):
        """Formats a sequence entry for display in the list box.

        Args:
            item (dict): A key definition containing `type`, `value`,
                and optional `modifiers`.

        Returns:
            str: Human-readable representation of the sequence entry.
        """

        item_type: str = item.get("type", "")
        value: str = item.get("value", "")
        modifiers: str = item.get("modifiers", "")

        if item_type == "text":
            return f"TEXT: {value}"

        if modifiers:
            return f"KEY: {modifiers} + {value}"

        return f"KEY: {value}"

    def _refresh_list(self):
        """Refreshes the visible list of sequence items."""
        self._field_sequence.Clear()

        for item in self._sequence:
            self._field_sequence.Append(self.format_item(item))

    def _on_add_text(self, _event):
        """Handles the Add Text button.

        Prompts the user for text input and appends a text entry to the
        send-keys sequence if confirmed.
        """
        dlg = wx.TextEntryDialog(self, "Enter text to send", "Add Text")

        if dlg.ShowModal() == wx.ID_OK:

            text = dlg.GetValue()

            payload: dict = {
                "type": "text",
                "value": text}
            self._sequence.append(payload)
            self._refresh_list()

            self._on_target_changed(None)

        dlg.Destroy()

    def _on_add_key(self, _event):
        """Handles the Add Key button.

        Opens the key selection dialog and appends the chosen key
        definition to the sequence.
        """
        dlg = SendkeyKeySelectionDialog(self)

        if dlg.ShowModal() == wx.ID_OK:
            key, modifiers = dlg.get_result()

            entry = {"type": "key",
                     "value": key,
                     "modifiers": modifiers}
            self._sequence.append(entry)

            self._refresh_list()

            self._on_target_changed(None)

        dlg.Destroy()

    def _on_remove(self, _event):
        """Removes the currently selected sequence item."""
        index = self._field_sequence.GetSelection()

        if index != wx.NOT_FOUND:
            del self._sequence[index]
            self._refresh_list()

            self._on_target_changed(None)

    def _on_move_up(self, _event):
        """Moves the selected sequence item one position upward."""
        index = self._field_sequence.GetSelection()

        if index > 0:
            self._sequence[index], self._sequence[index - 1] = \
                self._sequence[index - 1], self._sequence[index]

            self._refresh_list()
            self._field_sequence.SetSelection(index - 1)

    def _on_move_down(self, _event):
        """Moves the selected sequence item one position downward."""
        index = self._field_sequence.GetSelection()

        if index != wx.NOT_FOUND and index < len(self._sequence) - 1:

            self._sequence[index], self._sequence[index + 1] = \
                self._sequence[index + 1], self._sequence[index]

            self._refresh_list()
            self._field_sequence.SetSelection(index + 1)

    def _ok_event(self):
        target = self._field_target_element.GetValue()
        step_label = self._field_step_label.GetValue()

        if target:
            for item in self._sequence:
                if item.get("type") == "key":
                    wx.MessageBox(
                        "Key shortcuts cannot be used when a target element is"
                        "specified.\n"
                        "Please remove the key entries.",
                        "Invalid Send Keys Step",
                        wx.OK | wx.ICON_ERROR)
                    return

        payload: SendkeysPayload = SendkeysPayload(label=step_label,
                                                   target=target,
                                                   keys=self._sequence)
        self._event["payload"] = dataclasses.asdict(payload)
        self.changed = True
        self.EndModal(wx.ID_OK)

    def _on_edit_item(self, _event):
        """Handles editing an existing sequence entry."""

        index = self._field_sequence.GetSelection()

        if index == wx.NOT_FOUND:
            return

        item = self._sequence[index]

        if item.get("type") == "text":
            self._edit_text(index, item)

        elif item.get("type") == "key":
            self._edit_key(index, item)

    def _edit_text(self, index: int, item: dict):
        """Opens the text editor for an existing text entry."""

        dlg = wx.TextEntryDialog(
            self,
            "Edit text to send",
            "Edit Text",
            value=item.get("value", "")
        )

        if dlg.ShowModal() == wx.ID_OK:

            text = dlg.GetValue()

            self._sequence[index] = {
                "type": "text",
                "value": text
            }

            self._refresh_list()
            self._field_sequence.SetSelection(index)

        dlg.Destroy()

    def _edit_key(self, index: int, item: dict):
        """Opens the key editor for an existing key entry."""

        dlg = SendkeyKeySelectionDialog(
            self,
            key=item.get("value"),
            modifiers=item.get("modifiers")
        )

        if dlg.ShowModal() == wx.ID_OK:

            key, modifiers = dlg.get_result()

            self._sequence[index] = {
                "type": "key",
                "value": key,
                "modifiers": modifiers
            }

            self._refresh_list()
            self._field_sequence.SetSelection(index)

        dlg.Destroy()

    def _on_target_changed(self, _event):
        """Enforces rules when a target element is specified."""

        target = self._field_target_element.GetValue().strip()

        has_target = bool(target)
        button_enabled = not (has_target and self._sequence)

        # Disable key shortcuts if a target is present
        self._add_key_btn.Enable(not has_target)
        self._add_text_btn.Enable(button_enabled)
        self._up_btn.Enable(button_enabled)
        self._down_btn.Enable(button_enabled)

        # Optional: warn if the sequence already contains key entries
        if has_target:
            for item in self._sequence:
                if item.get("type") == "key":
                    wx.MessageBox(
                        "Key shortcuts cannot be used when a target element "
                        "is specified. Please remove the key entries.",
                        "Invalid Send Keys Configuration",
                        wx.OK | wx.ICON_WARNING
                    )
                    break
