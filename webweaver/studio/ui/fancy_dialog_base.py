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
from typing import Callable
import wx


class DialogHeader(wx.Panel):
    """
    Header panel used in dialogs to display an icon, title, and description.

    This component is intended to provide a consistent visual header for
    dialogs. It displays a large icon on the left and a bold title with a
    description on the right.
    """
    # pylint: disable=too-few-public-methods

    def __init__(self, parent, title, description, icon=wx.ART_INFORMATION):
        """
        Initialize the dialog header.

        Args:
            parent (wx.Window):
                The parent window for the panel.
            title (str):
                The main title displayed in bold.
            description (str):
                A short descriptive text displayed below the title.
            icon (wx.ArtID, optional):
                The wxWidgets art provider identifier used to retrieve
                the icon. Defaults to wx.ART_INFORMATION.
        """
        super().__init__(parent)

        main = wx.BoxSizer(wx.HORIZONTAL)

        bmp = wx.ArtProvider.GetBitmap(icon, wx.ART_OTHER, (32, 32))
        icon_ctrl = wx.StaticBitmap(self, bitmap=bmp)

        text_sizer = wx.BoxSizer(wx.VERTICAL)

        title_text = wx.StaticText(self, label=title)
        font = title_text.GetFont()
        font.MakeBold()
        font.SetPointSize(font.GetPointSize() + 4)
        title_text.SetFont(font)

        desc_text = wx.StaticText(self, label=description)

        text_sizer.Add(title_text, 0, wx.BOTTOM, 4)
        text_sizer.Add(desc_text, 0)

        main.Add(icon_ctrl, 0, wx.ALL | wx.ALIGN_TOP, 12)
        main.Add(text_sizer, 1, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 12)

        self.SetSizer(main)


class FancyDialogBase(wx.Dialog):
    """
    Base class for dialogs with a styled header and structured content area.

    This dialog provides a reusable layout consisting of:
        - A header with title and description
        - A separator line
        - A flexible two-column content area for form fields
        - Standard OK/Cancel buttons

    Subclasses can populate the dialog using `add_field()` and `add_help()`,
    and override `_validate()` to perform validation before the dialog closes.
    """

    def __init__(self,
                 parent: wx.Window,
                 title: str,
                 header_title: str,
                 header_desc: str):
        """
        Initialize the base dialog layout.

        Args:
            parent (wx.Window):
                The parent window for the dialog.
            title (str):
                The window title of the dialog.
            header_title (str):
                The title displayed in the dialog header.
            header_desc (str):
                The descriptive text displayed in the dialog header.
        """
        super().__init__(parent, title=title)

        self._label_width = 110

        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # Header
        header = DialogHeader(self, header_title, header_desc)
        main_sizer.Add(header, 0, wx.EXPAND)

        # Divider
        line = wx.StaticLine(self)
        main_sizer.Add(line, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 5)

        # Content area
        self.content = wx.Panel(self)
        self.content_sizer = wx.BoxSizer(wx.VERTICAL)
        self.content.SetSizer(self.content_sizer)

        main_sizer.Add(self.content,
                       0,
                       wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP,
                       15)

        btn_sizer = self.CreateButtonSizer(wx.OK | wx.CANCEL)
        main_sizer.Add(btn_sizer, 0, wx.ALL | wx.ALIGN_RIGHT, 6)

        self.SetSizer(main_sizer)

        self.Bind(wx.EVT_BUTTON, self._on_ok, id=wx.ID_OK)

    def add_field(self,
                  label: str,
                  control: Callable[[wx.Window], wx.Window]):
        """
        Add a labeled input field to the dialog content area.

        The control will be created and added to the two-column layout,
        with the label on the left and the control on the right.

        Args:
            label (str):
                The label displayed next to the control.
            control (Callable[[wx.Window], wx.Window]):
                A callable used to create the control. It will be called
                with the content panel as its parent.

        Returns:
            wx.Window:
                The created control instance.
        """
        row = wx.BoxSizer(wx.HORIZONTAL)

        label_ctrl = wx.StaticText(self.content, label=label)
        label_ctrl.SetMinSize((self._label_width, -1))

        ctrl = control(self.content)

        row.Add(label_ctrl, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 10)
        row.Add(ctrl, 1, wx.EXPAND)

        self.content_sizer.Add(row, 0, wx.EXPAND | wx.BOTTOM, 6)

        return ctrl

    def add_full_width_field(self,
                             label: str,
                             control_factory: Callable[[wx.Window], wx.Window]):
        block = wx.BoxSizer(wx.VERTICAL)

        label_ctrl = wx.StaticText(self.content, label=label)
        ctrl = control_factory(self.content)

        block.Add(label_ctrl, 0, wx.BOTTOM, 6)
        block.Add(ctrl, 1, wx.EXPAND)

        self.content_sizer.Add(block, 1, wx.EXPAND | wx.BOTTOM, 10)

        return ctrl

    def add_help(self, text: str):
        """
        Add a help or tips section to the dialog.

        A boxed section labeled "Tips" will be inserted into the dialog
        layout containing the provided explanatory text.

        Args:
            text (str):
                The help text to display inside the tips section.

        Returns:
            None
        """
        box = wx.StaticBox(self, label="Tips")
        sizer = wx.StaticBoxSizer(box, wx.VERTICAL)

        tip = wx.StaticText(self, label=text)
        tip.Wrap(350)

        sizer.Add(tip, 0, wx.ALL, 8)

        self.GetSizer().Insert(2,
                               sizer,
                               0,
                               wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP,
                               10)

    def finalise(self):
        self.content_sizer.AddStretchSpacer()
        self.content.Layout()
        self.Layout()
        self.Fit()
        self.SetMinSize(self.GetSize())

    def _validate(self):
        """
        Validate the dialog inputs before closing.

        Subclasses can override this method to implement validation logic.

        Returns:
            bool:
                True if the dialog can close, otherwise False.
        """
        return True

    def _ok_event(self):
        """
        OK button press event.

        Subclasses can override this method to implement OK event logic.
        """

    def _on_ok(self, _event):
        """
        Handle the OK button click.

        If validation succeeds, the dialog will close with wx.ID_OK.

        Args:
            _event (wx.CommandEvent):
                The button event triggered by the OK button.
        """
        if self._validate():
            self.EndModal(wx.ID_OK)

        self._ok_event()
