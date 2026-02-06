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
from ..solution_create_wizard.solution_create_wizard_data import \
    SolutionCreateWizardData
from ..solution_create_wizard.solution_wizard_base import (SolutionWizardBase,
                                                           NextButtonType)


class WizardFinishPage(SolutionWizardBase):
    """
    Final page of the solution creation wizard.

    This page presents a summary / closing message to the user and provides
    a Finish button to complete the wizard. When the user clicks Finish,
    the wizard closes and signals successful completion.

    This page does not navigate to another wizard page.
    """
    # pylint: disable=too-few-public-methods

    NEXT_WIZARD_PAGE = None

    TITLE_STR: str = "Almost there"
    SUBTITLE_STR: str = (
        "Read what's next and then click Finish to create "
        "your solution and get started.")

    def __init__(self,
                 parent: wx.Window,
                 data: SolutionCreateWizardData):
        """
        Create the final wizard page.

        Args:
            parent (wx.Window): The parent window that owns this wizard page.
            data (SolutionCreateWizardData): Shared wizard data object used to
                store and retrieve information collected throughout the wizard.
        """
        super().__init__("Set up your web test",
                         parent, data, 3)

        # Header
        self._create_header(self.TITLE_STR, self.SUBTITLE_STR)

        # Button bar
        self._create_buttons_bar(self._on_next_click_event,
                                 NextButtonType.FINISH_BUTTON)

        self.SetSizerAndFit(self._main_sizer)
        self.CentreOnParent()

    def _on_next_click_event(self, _event: wx.CommandEvent):
        """
        Handle the Finish button click event.

        Ends the wizard dialog and signals successful completion by returning
        wx.ID_OK to the caller.
        """
        self.EndModal(wx.ID_OK)
