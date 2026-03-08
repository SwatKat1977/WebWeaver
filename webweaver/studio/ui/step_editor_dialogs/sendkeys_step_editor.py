import dataclasses
import wx
from webweaver.studio.persistence.recording_document import (
    SendkeysKeyDefinition, SendkeysPayload)
from webweaver.studio.ui.step_editor_dialogs.sendkey_key_selection_dialog \
    import SendkeyKeySelectionDialog


class SendkeysStepEditor(wx.Dialog):

    KEY_CHOICES = [
        "ENTER", "TAB", "ESCAPE", "BACKSPACE", "DELETE",
        "SPACE", "ARROW_UP", "ARROW_DOWN",
        "ARROW_LEFT", "ARROW_RIGHT", "HOME", "END"
    ]

    def __init__(self, parent, _index: int, event: dict = None):
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
        self._remove_btn = wx.Button(panel, label="Remove")
        self._up_btn = wx.Button(panel, label="Move Up")
        self._down_btn = wx.Button(panel, label="Move Down")

        btn_sizer.Add(self._add_text_btn, 0, wx.ALL, 5)
        btn_sizer.Add(self._add_key_btn, 0, wx.ALL, 5)
        btn_sizer.Add(self._remove_btn, 0, wx.ALL, 5)
        btn_sizer.Add(self._up_btn, 0, wx.ALL, 5)
        btn_sizer.Add(self._down_btn, 0, wx.ALL, 5)

        main_sizer.Add(btn_sizer, 0, wx.CENTER)

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

        self.refresh_list()

    def format_item(self, item: dict):
        type: str = item.get("type", "")
        value: str = item.get("value", "")
        modifiers: str = item.get("modifiers", "")

        if type == "text":
            return f"TEXT: {value}"

        if modifiers:
            return f"KEY: {modifiers} + {value}"

        return f"KEY: {value}"

    def refresh_list(self):

        self._sequence_list.Clear()

        for item in self._sequence:
            self._sequence_list.Append(self.format_item(item))

    def _on_add_text(self, event):

        dlg = wx.TextEntryDialog(self, "Enter text to send", "Add Text")

        if dlg.ShowModal() == wx.ID_OK:

            text = dlg.GetValue()

            self._sequence.append(SendkeysKeyDefinition(type="text",
                                                        value=text))
            self.refresh_list()

        dlg.Destroy()

    def _on_add_key(self, _event):

        dlg = SendkeyKeySelectionDialog(self)

        if dlg.ShowModal() == wx.ID_OK:
            key, modifiers = dlg.get_result()

            entry = {"type": "key",
                     "value": key,
                     "modifiers": modifiers}
            self._sequence.append(entry)

            self.refresh_list()

        dlg.Destroy()

    def _on_remove(self, _event):

        index = self._sequence_list.GetSelection()

        if index != wx.NOT_FOUND:
            del self._sequence[index]
            self.refresh_list()

    def _on_move_up(self, _event):

        index = self._sequence_list.GetSelection()

        if index > 0:
            self._sequence[index], self._sequence[index - 1] = \
                self._sequence[index - 1], self._sequence[index]

            self.refresh_list()
            self._sequence_list.SetSelection(index - 1)

    def _on_move_down(self, _event):
        index = self._sequence_list.GetSelection()

        if index != wx.NOT_FOUND and index < len(self._sequence) - 1:

            self._sequence[index], self._sequence[index + 1] = \
                self._sequence[index + 1], self._sequence[index]

            self.refresh_list()
            self._sequence_list.SetSelection(index + 1)

    def _on_save(self, _event):
        target = self._target_input.GetValue()
        payload: SendkeysPayload = SendkeysPayload(target=target,
                                                   keys=self._sequence)
        self._event["payload"] = dataclasses.asdict(payload)
        self.changed = True
        self.EndModal(wx.ID_OK)
