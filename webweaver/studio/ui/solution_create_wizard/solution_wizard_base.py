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
import enum
import wx
from webweaver.studio.wizard_step_indicator import WizardStepIndicator
from webweaver.studio.ui.solution_create_wizard.solution_create_wizard_data \
    import SolutionCreateWizardData
from webweaver.studio.ui.solution_create_wizard.solution_widget_ids import \
    SOLUTION_WIZARD_BACK_BUTTON_ID


class NextButtonType(enum.Enum):
    """
    Enumeration describing the type of "next" button to display in a wizard.

    This is used to control whether the wizard shows a normal "Next" button
    or a final "Finish" button on a given wizard page.
    """
    NEXT_BUTTON = enum.auto()
    FINISH_BUTTON = enum.auto()


class SolutionWizardBase(wx.Dialog):
    """
    Base class for all pages in the Solution Creation Wizard.

    This class provides common UI infrastructure shared by all wizard pages,
    including:

    - The step indicator at the top of the dialog
    - A standard header layout (icon, title, subtitle)
    - A standard bottom button bar (Cancel / Next)
    - A main vertical sizer (`self._main_sizer`) into which derived pages
      insert their own content

    Each concrete wizard page should inherit from this class, call the base
    constructor, and then populate `self._main_sizer` with its page-specific
    controls before calling `SetSizerAndFit`.

    The wizard is modal: pages should call `EndModal(wx.ID_OK)` to advance or
    `EndModal(wx.ID_CANCEL)` to cancel.
    """
    # pylint: disable=too-few-public-methods

    # Steps for solution creation wizard indicator
    STEPS = [
        "Basic solution info",
        "Browser selection",
        "Configure behaviour",
        "Finish"
    ]

    def __init__(self,
                 wizard_title: str,
                 parent: wx.Window, data: SolutionCreateWizardData,
                 step_index: int):
        """
        Construct a new wizard page.

        Parameters
        ----------
        wizard_title : str
            The window title for this wizard page.
        parent : wx.Window
            The parent window.
        data : SolutionCreateWizardData
            Shared data object used to accumulate the user's choices across
            all wizard pages.
        step_index : int
            Index of the current step to highlight in the step indicator.
        """
        super().__init__(parent,
                         title=wizard_title,
                         style=wx.DEFAULT_DIALOG_STYLE)
        self._data = data

        self._main_sizer: wx.BoxSizer = wx.BoxSizer(wx.VERTICAL)

        step_indicator: WizardStepIndicator = WizardStepIndicator(
            self, self.STEPS, step_index)
        self._main_sizer.Add(step_indicator, 0, wx.EXPAND | wx.ALL, 10)

    def _create_header(self, title_str: str, subtitle_str: str):
        """
        Create and add a standard wizard page header.

        The header consists of:
        - A small icon on the left
        - A bold title
        - A smaller, grey subtitle beneath the title

        The constructed header is automatically added to `self._main_sizer`.

        Parameters
        ----------
        title_str : str
            The main title text for the page.
        subtitle_str : str
            The subtitle text displayed under the main title.
        """
        header: wx.BoxSizer = wx.BoxSizer(wx.HORIZONTAL)
        icon: wx.StaticBitmap = wx.StaticBitmap(
            self,
            wx.ID_ANY,
            wx.ArtProvider.GetBitmap(wx.ART_TIP,
                                     wx.ART_OTHER,
                                     wx.Size(32, 32)))
        header.Add(icon, 0, wx.ALL, 10)

        # Text area (vertical sizer)
        header_area: wx.BoxSizer = wx.BoxSizer(wx.VERTICAL)

        # Title
        title: wx.StaticText = wx.StaticText(self, wx.ID_ANY, title_str)
        title.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT,
                              wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))

        # Subtitle
        subtitle: wx.StaticText = wx.StaticText(self, wx.ID_ANY, subtitle_str)
        subtitle.SetForegroundColour(wx.Colour(100, 100, 100))
        header_area.Add(title, 0)
        header_area.Add(subtitle, 0, wx.TOP, 4)

        # Add text area into header sizer
        header.Add(header_area, 1, wx.ALIGN_CENTER_VERTICAL)

        # Add the whole header to main sizer
        self._main_sizer.Add(header, 0, wx.LEFT | wx.RIGHT, 10)

    def _create_buttons_bar(self,
                            validator_method=None,
                            next_type=NextButtonType.NEXT_BUTTON,
                            back_button=True):
        """
        Create and add the standard bottom button bar.

        The button bar contains:
        - A Cancel button, which always closes the wizard with wx.ID_CANCEL
        - A Next button, which calls the supplied validator method

        The validator method is expected to perform any input validation and
        call `EndModal(wx.ID_OK)` if the page is valid.

        The constructed button bar is automatically added to
        `self._main_sizer`.

        Parameters
        ----------
        validator_method : callable or None
            Method to bind to the Next button's click event. This method should
            accept a wx.Event parameter and is responsible for validating the
            page and calling EndModal(wx.ID_OK) on success.
        """
        button_bar_sizer: wx.BoxSizer = wx.BoxSizer(wx.HORIZONTAL)
        # Spacer to push buttons to the right
        button_bar_sizer.AddStretchSpacer()

        # Cancel button
        btn_cancel: wx.Button = wx.Button(self, wx.ID_CANCEL, "Cancel")
        btn_cancel.Bind(wx.EVT_BUTTON, lambda evt: self.EndModal(wx.ID_CANCEL))
        button_bar_sizer.Add(btn_cancel, 0, wx.RIGHT, 10)

        # Back button
        if back_button:
            btn_back: wx.Button = wx.Button(self,
                                            SOLUTION_WIZARD_BACK_BUTTON_ID,
                                            "Back")
            btn_back.Bind(wx.EVT_BUTTON,
                          lambda evt: self.EndModal(SOLUTION_WIZARD_BACK_BUTTON_ID))
            button_bar_sizer.Add(btn_back, 0, wx.RIGHT, 10)

        # Next button
        next_str = "Next" if next_type == NextButtonType.NEXT_BUTTON \
            else "Finish"
        btn_next: wx.Button = wx.Button(self, wx.ID_OK, next_str)
        btn_next.Bind(wx.EVT_BUTTON, validator_method)
        button_bar_sizer.Add(btn_next, 0)

        # Add to main layout
        self._main_sizer.Add(button_bar_sizer, 0, wx.EXPAND | wx.ALL, 10)
