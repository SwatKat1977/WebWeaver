"""
This source file is part of Web Weaver
For the latest info, see https://github.com/SwatKat1977/WebWeaver

Copyright 2025 SwatKat1977

    This program is free software : you can redistribute it and /or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.If not, see < https://www.gnu.org/licenses/>.
"""
import wx


class WizardBasePage(wx.Panel):
    """
    Base class for all wizard pages.

    Each page in the wizard should inherit from `WizardBasePage` and provide
    its own UI layout as well as any validation logic needed before progressing
    to the next step. The wizard uses this base class to manage page titles,
    subtitles, validation flow, and lifecycle callbacks (`on_enter` and
    `on_leave`).

    Parameters
    ----------
    parent : wx.Window
        The parent window or container panel that holds this page.
    wizard : WizardDialog
        Reference to the parent wizard controller. Provides shared data and
        access to navigation.
    title : str
        Title text displayed in the wizard header when this page is active.
    subtitle : str
        Subtitle text displayed beneath the title.

    Notes
    -----
    Subclasses are expected to:
        - Build their UI inside the panel.
        - Override `validate()` to enforce required fields.
        - Optionally override `on_enter()` and `on_leave()` to update state.
    """

    def __init__(self, parent, wizard, title: str, subtitle: str):
        """
        Initialize a new wizard page.

        Parameters
        ----------
        parent : wx.Window
            The parent panel or window that will contain the page.
        wizard : WizardDialog
            The wizard controller managing navigation and shared data.
        title : str
            Title text for this page, shown in the wizard header.
        subtitle : str
            Subtitle text providing additional context.
        """
        super().__init__(parent)
        self.wizard = wizard
        self._title = title
        self._subtitle = subtitle

    @property
    def title(self) -> str:
        """
        Return the title text for this wizard page.

        Returns
        -------
        str
            The page title displayed in the wizard header.
        """
        return self._title

    @property
    def subtitle(self) -> str:
        """
        Return the subtitle text for this wizard page.

        Returns
        -------
        str
            Additional descriptive text shown beneath the title.
        """
        return self._subtitle

    def validate(self) -> bool:
        """
        Validate the page before advancing to the next one.

        Returns
        -------
        bool
            True if the page is valid and navigation should proceed.
            False to block navigation (e.g., missing required fields).

        Notes
        -----
        Subclasses should override this method to implement validation
        logic specific to the page's input fields.
        """
        return True

    def on_enter(self):
        """
        Called when the wizard navigates to this page.

        Notes
        -----
        Subclasses may override this method to refresh UI state,
        load data, or reset controls when the page becomes active.
        """
        pass

    def on_leave(self):
        """
        Called when the wizard navigates away from this page.

        Notes
        -----
        Subclasses may override this method to store state, commit data,
        or perform cleanup before the page is hidden.
        """
        pass
