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
from webweaver.studio.persistence.recording_document import (
    SendkeysKeyDefinition, SendkeysPayload)
from webweaver.studio.ui.step_editor_dialogs.sendkey_key_selection_dialog \
    import SendkeyKeySelectionDialog


class SendkeysStepEditor(wx.Dialog):
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

    def __init__(self, parent, _index: int, event: dict = None):
        """Initializes the Send Keys step editor dialog.

        Args:
            parent (wx.Window): Parent window that owns this dialog.
            _index (int): Index of the step being edited. Currently unused
                but retained for interface consistency.
            event (dict, optional): Existing event definition containing a
                payload to populate the dialog with. Defaults to None.
        """
        super().__init__(parent, title="Send Keys", size=(500, 400))

        self._event = event
        self._sequence = []
        self.changed = False

        panel = wx.Panel(self)
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # Target
        target_label = wx.StaticText(panel, label="Target Element")
        self._target_input = wx.TextCtrl(panel)

        main_sizer.Add(target_label, 0, wx.ALL, 5)
        main_sizer.Add(self._target_input, 0, wx.EXPAND | wx.ALL, 5)

        # Sequence list
        self._sequence_list = wx.ListBox(panel)
        self._sequence_list.Bind(wx.EVT_LISTBOX_DCLICK, self._on_edit_item)

        if event and "payload" in event:
            payload = event["payload"]

            self._sequence = list(payload.get("keys", []))
            self._target_input.SetValue(payload.get("target", ""))

        main_sizer.Add(wx.StaticText(panel, label="Sequence"), 0, wx.ALL, 5)
        main_sizer.Add(self._sequence_list, 1, wx.EXPAND | wx.ALL, 5)

        # Buttons
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self._add_text_btn = wx.Button(panel, label="Add Text")
        self._add_key_btn = wx.Button(panel, label="Add Key")
        self._add_key_btn.SetToolTip(
            "Key shortcuts are only available when no target element is "
            "specified.")
        self._remove_btn = wx.Button(panel, label="Remove")
        self._up_btn = wx.Button(panel, label="Move Up")
        self._down_btn = wx.Button(panel, label="Move Down")

        btn_sizer.Add(self._add_text_btn, 0, wx.ALL, 5)
        btn_sizer.Add(self._add_key_btn, 0, wx.ALL, 5)
        btn_sizer.Add(self._remove_btn, 0, wx.ALL, 5)
        btn_sizer.Add(self._up_btn, 0, wx.ALL, 5)
        btn_sizer.Add(self._down_btn, 0, wx.ALL, 5)

        main_sizer.Add(btn_sizer, 0, wx.CENTER)

        self._target_input.Bind(wx.EVT_TEXT, self._on_target_changed)

        # Save/Cancel
        action_sizer = wx.StdDialogButtonSizer()

        save_btn = wx.Button(panel, wx.ID_OK)
        cancel_btn = wx.Button(panel, wx.ID_CANCEL)

        action_sizer.AddButton(save_btn)
        action_sizer.AddButton(cancel_btn)
        action_sizer.Realize()

        main_sizer.Add(action_sizer, 0, wx.ALIGN_RIGHT | wx.ALL, 10)

        panel.SetSizer(main_sizer)

        # Bindings
        self._add_text_btn.Bind(wx.EVT_BUTTON, self._on_add_text)
        self._add_key_btn.Bind(wx.EVT_BUTTON, self._on_add_key)
        self._remove_btn.Bind(wx.EVT_BUTTON, self._on_remove)
        self._up_btn.Bind(wx.EVT_BUTTON, self._on_move_up)
        self._down_btn.Bind(wx.EVT_BUTTON, self._on_move_down)
        save_btn.Bind(wx.EVT_BUTTON, self._on_save)

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
        self._sequence_list.Clear()

        for item in self._sequence:
            self._sequence_list.Append(self.format_item(item))

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
        index = self._sequence_list.GetSelection()

        if index != wx.NOT_FOUND:
            del self._sequence[index]
            self._refresh_list()

            self._on_target_changed(None)

    def _on_move_up(self, _event):
        """Moves the selected sequence item one position upward."""
        index = self._sequence_list.GetSelection()

        if index > 0:
            self._sequence[index], self._sequence[index - 1] = \
                self._sequence[index - 1], self._sequence[index]

            self._refresh_list()
            self._sequence_list.SetSelection(index - 1)

    def _on_move_down(self, _event):
        """Moves the selected sequence item one position downward."""
        index = self._sequence_list.GetSelection()

        if index != wx.NOT_FOUND and index < len(self._sequence) - 1:

            self._sequence[index], self._sequence[index + 1] = \
                self._sequence[index + 1], self._sequence[index]

            self._refresh_list()
            self._sequence_list.SetSelection(index + 1)

    def _on_save(self, _event):
        """Saves the edited send-keys sequence into the event payload.

        The target element and sequence are serialized into a
        ``SendkeysPayload`` object and written back into the provided
        event dictionary.
        """
        target = self._target_input.GetValue()

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

        payload: SendkeysPayload = SendkeysPayload(target=target,
                                                   keys=self._sequence)
        self._event["payload"] = dataclasses.asdict(payload)
        self.changed = True
        self.EndModal(wx.ID_OK)

    def _on_edit_item(self, _event):
        """Handles editing an existing sequence entry."""

        index = self._sequence_list.GetSelection()

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
            self._sequence_list.SetSelection(index)

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
            self._sequence_list.SetSelection(index)

        dlg.Destroy()

    def _on_target_changed(self, _event):
        """Enforces rules when a target element is specified."""

        target = self._target_input.GetValue().strip()

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
