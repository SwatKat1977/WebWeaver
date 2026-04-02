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
from wx.lib import scrolledpanel
from webweaver.studio.browser_launch_options import BrowserLaunchOptions, WindowSize
from webweaver.studio.studio_solution import StudioSolution
from webweaver.studio.ui.framework.settings_page import (SettingsPage,
                                                         ValidationResult)


class BrowserSettingsPage(SettingsPage):
    """Settings page for configuring browser behaviour and launch options.

    This page provides controls for common browser runtime settings such as
    privacy mode, extension handling, notification suppression, and advanced
    automation-related flags. It also allows configuration of the browser
    window size and optional user agent override.
    """
    # pylint: disable=too-many-instance-attributes

    def __init__(self, parent, context: StudioSolution):
        """Initialise the BrowserSettingsPage UI.

        Args:
            parent: The parent wx window.
            context (StudioSolution): The solution context providing
                current browser configuration and receiving updates.
        """
        super().__init__(parent)
        self._context: StudioSolution = context

        scrolled = scrolledpanel.ScrolledPanel(self)

        outer = wx.BoxSizer(wx.VERTICAL)
        outer.Add(scrolled, 1, wx.EXPAND)

        # ---- Content container ----
        content = wx.BoxSizer(wx.VERTICAL)

        # ---- Basic behaviour section ----
        self.add_section_title(scrolled, "Basic behaviour", content)

        self._private_mode = wx.CheckBox(
            scrolled, wx.ID_ANY, "Private / Incognito mode (recommended)")
        content.Add(self._private_mode, 0, wx.BOTTOM, 10)

        self._disable_extensions = wx.CheckBox(
            scrolled, wx.ID_ANY, "Disable extensions (recommended)")
        content.Add(self._disable_extensions, 0, wx.BOTTOM, 10)

        self._disable_notifications = wx.CheckBox(
            scrolled, wx.ID_ANY, "Disable notifications (recommended)")
        content.Add(self._disable_notifications, 0, wx.BOTTOM, 10)

        self._ignore_cert_errors = wx.CheckBox(
            scrolled, wx.ID_ANY, "Ignore certificate errors (advanced)")
        content.Add(self._ignore_cert_errors, 0, wx.BOTTOM, 10)

        self._disable_automation_controlled_feature = wx.CheckBox(
            scrolled, wx.ID_ANY, "Disable Automation Controlled Feature (advanced)")
        content.Add(self._disable_automation_controlled_feature, 0, wx.BOTTOM, 10)

        # ===== Browser size section title =====
        self.add_section_title(scrolled, "Browser size", content)

        # ---- Window size section ----
        window_label = wx.StaticText(scrolled, label="Browser window size")
        window_label.SetFont(window_label.GetFont().Bold())
        content.Add(window_label, 0, wx.EXPAND | wx.BOTTOM, 5)

        self._window_size_default: wx.RadioButton = wx.RadioButton(
            scrolled, wx.ID_ANY, "Default size", style=wx.RB_GROUP)
        content.Add(self._window_size_default, 0, wx.ALL, 5)

        self._window_size_maximised: wx.RadioButton = wx.RadioButton(
            scrolled, wx.ID_ANY, "Maximised (Recommended)")
        content.Add(self._window_size_maximised, 0, wx.ALL, 5)

        self._window_size_custom: wx.RadioButton = wx.RadioButton(
            scrolled, wx.ID_ANY, "Custom size")
        content.Add(self._window_size_custom, 0, wx.ALL, 5)

        self._window_size_width: wx.TextCtrl = wx.TextCtrl(
            scrolled, wx.ID_ANY, "1280", size=(60, -1))
        self._window_size_height: wx.TextCtrl = wx.TextCtrl(
            scrolled, wx.ID_ANY, "800", size=(60, -1))
        size_sizer: wx.BoxSizer = wx.BoxSizer(wx.HORIZONTAL)
        size_sizer.Add(self._window_size_width, 0, wx.RIGHT, 5)
        size_sizer.Add(wx.StaticText(scrolled,  wx.ID_ANY, "×"),
                       0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        size_sizer.Add(self._window_size_height, 0)
        content.Add(size_sizer, 0, wx.LEFT | wx.BOTTOM, 10)

        # ===== Advanced browser section title =====
        self.add_section_title(scrolled, "Advanced browser options", content)

        # ---- Advanced browser section ----
        agent_override_label = wx.StaticText(scrolled, label="User agent override")
        agent_override_label.SetFont(agent_override_label.GetFont().Bold())
        content.Add(agent_override_label, 0, wx.EXPAND | wx.BOTTOM, 5)
        self._advanced_user_agent: wx.TextCtrl = wx.TextCtrl(scrolled)
        content.Add(self._advanced_user_agent, 0, wx.EXPAND | wx.BOTTOM | wx.RIGHT, 12)

        self._window_size_default.Bind(
            wx.EVT_RADIOBUTTON,
            lambda evt: self._sync_window_size_state())
        self._window_size_maximised.Bind(
            wx.EVT_RADIOBUTTON,
            lambda evt: self._sync_window_size_state())
        self._window_size_custom.Bind(
            wx.EVT_RADIOBUTTON,
            lambda evt: self._sync_window_size_state())

        self._sync_window_size_state()

        # ---- Final wiring ----

        scrolled.SetSizer(content)
        scrolled.SetupScrolling(scroll_x=False)

        self.SetSizer(outer)

    def load(self):
        """Load browser settings from the solution context into the UI.

        This method reads the current ``BrowserLaunchOptions`` from the
        associated ``StudioSolution`` context and updates all UI controls
        to reflect the stored configuration, including:

            - Basic behaviour flags (privacy, extensions, notifications, etc.)
            - User agent override
            - Browser window size mode and dimensions

        The window size controls are synchronised after loading to ensure
        the correct fields are enabled or disabled.
        """
        browser_opts: BrowserLaunchOptions = self._context.browser_launch_options
        self._private_mode.SetValue(browser_opts.private_mode)
        self._disable_extensions.SetValue(browser_opts.disable_extensions)
        self._disable_notifications.SetValue(browser_opts.disable_notifications)
        self._ignore_cert_errors.SetValue(
            browser_opts.ignore_certificate_errors)
        self._disable_automation_controlled_feature.SetValue(
            browser_opts.disable_automation_controlled_feature)

        user_agent = browser_opts.user_agent if browser_opts.user_agent else ""
        self._advanced_user_agent.SetValue(user_agent)

        if browser_opts.maximised:
            self._window_size_maximised.SetValue(1)

        elif browser_opts.window_size:
            self._window_size_custom.SetValue(1)
            self._window_size_width.SetValue(str(browser_opts.window_size.width))
            self._window_size_height.SetValue(str(browser_opts.window_size.height))

        else:
            self._window_size_default.SetValue(1)

        self._sync_window_size_state()

    def _sync_window_size_state(self) -> None:
        """Synchronise the enabled state of custom window size controls.

        Enables or disables the width and height input fields depending on
        whether the "Custom size" radio option is selected. When custom size
        is not selected, these fields are disabled to prevent user input.
        """
        custom: bool = self._window_size_custom.GetValue()
        self._window_size_width.Enable(custom)
        self._window_size_height.Enable(custom)

    def validate(self) -> ValidationResult:
        # No validation needed for checkboxes
        return ValidationResult(True)

    def apply(self):
        self._context.browser_launch_options.private_mode = \
            self._private_mode.GetValue()
        self._context.browser_launch_options.disable_extensions = \
            self._disable_extensions.GetValue()
        self._context.browser_launch_options.disable_notifications = \
            self._disable_notifications.GetValue()
        self._context.browser_launch_options.ignore_certificate_errors = \
            self._ignore_cert_errors.GetValue()
        self._context.browser_launch_options.disable_automation_controlled_feature = \
            self._disable_automation_controlled_feature.GetValue()
        self._context.browser_launch_options.user_agent = \
            self._advanced_user_agent.GetValue()

        # Browser window size : Maximised
        if self._window_size_maximised.GetValue():
            self._context.browser_launch_options.maximised = True
            self._context.browser_launch_options.window_size = None

        # Browser window size : Custom size
        elif self._window_size_custom.GetValue():
            self._context.browser_launch_options.maximised = False

            self._context.browser_launch_options.window_size = \
                WindowSize(width=int(self._window_size_width.GetValue()),
                           height=int(self._window_size_height.GetValue()))

        # Browser window : Default size
        else:
            self._context.browser_launch_options.maximised = False
            self._context.browser_launch_options.window_size = None
