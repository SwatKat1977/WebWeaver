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
import wx


class SendkeyKeySelectionDialog(wx.Dialog):
    """Dialog that allows the user to select a keyboard key and modifiers.

    This dialog is used when building a send-keys sequence. The user can
    choose a special key from a predefined list and optionally apply
    modifier keys such as CTRL, ALT, SHIFT, or META.

    Attributes:
        KEY_CHOICES (list[str]): List of available special keys that can be
            selected.
        key_choice (wx.Choice): Dropdown widget used to select the base key.
        ctrl (wx.CheckBox): Checkbox indicating whether the CTRL modifier
            should be applied.
        alt (wx.CheckBox): Checkbox indicating whether the ALT modifier
            should be applied.
        shift (wx.CheckBox): Checkbox indicating whether the SHIFT modifier
            should be applied.
        meta (wx.CheckBox): Checkbox indicating whether the META modifier
            should be applied.
    """
    # pylint: disable=too-few-public-methods

    KEY_CHOICES = [
        "ENTER", "TAB", "ESCAPE", "BACKSPACE", "DELETE",
        "SPACE", "ARROW_UP", "ARROW_DOWN",
        "ARROW_LEFT", "ARROW_RIGHT",
        "HOME", "END"
    ]

    def __init__(self, parent):
        """Initializes the key selection dialog.

        Args:
            parent (wx.Window): Parent window that owns this dialog.
        """
        super().__init__(parent, title="Select Key", size=(300, 250))

        panel = wx.Panel(self)
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # Key dropdown
        main_sizer.Add(wx.StaticText(panel, label="Key"), 0, wx.ALL, 5)

        self.key_choice = wx.Choice(panel, choices=self.KEY_CHOICES)
        self.key_choice.SetSelection(0)

        main_sizer.Add(self.key_choice, 0, wx.EXPAND | wx.ALL, 5)

        # Modifiers
        main_sizer.Add(wx.StaticText(panel, label="Modifiers"), 0, wx.ALL, 5)

        self.ctrl = wx.CheckBox(panel, label="CTRL")
        self.alt = wx.CheckBox(panel, label="ALT")
        self.shift = wx.CheckBox(panel, label="SHIFT")
        self.meta = wx.CheckBox(panel, label="META")

        main_sizer.Add(self.ctrl, 0, wx.ALL, 2)
        main_sizer.Add(self.alt, 0, wx.ALL, 2)
        main_sizer.Add(self.shift, 0, wx.ALL, 2)
        main_sizer.Add(self.meta, 0, wx.ALL, 2)

        # Buttons
        btn_sizer = wx.StdDialogButtonSizer()

        ok_btn = wx.Button(panel, wx.ID_OK)
        cancel_btn = wx.Button(panel, wx.ID_CANCEL)

        btn_sizer.AddButton(ok_btn)
        btn_sizer.AddButton(cancel_btn)
        btn_sizer.Realize()

        main_sizer.Add(btn_sizer, 0, wx.ALIGN_RIGHT | wx.ALL, 10)

        panel.SetSizer(main_sizer)

    def get_result(self):
        """Returns the selected key and modifier combination.

        The selected key is taken from the dropdown list, while the modifier
        string is constructed from the selected checkboxes.

        Returns:
            tuple[str, Optional[str]]: A tuple containing:
                - key: The selected key name.
                - modifiers: A '+'-joined string of modifiers (e.g. "CTRL+SHIFT")
                  or ``None`` if no modifiers were selected.
        """
        key = self.key_choice.GetStringSelection()

        modifiers = []

        if self.ctrl.GetValue():
            modifiers.append("CTRL")

        if self.alt.GetValue():
            modifiers.append("ALT")

        if self.shift.GetValue():
            modifiers.append("SHIFT")

        if self.meta.GetValue():
            modifiers.append("META")

        if modifiers:
            return key, "+".join(modifiers)

        return key, None
