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
import wx.lib.scrolledpanel as scrolledpanel
from webweaver.studio.studio_solution import StudioSolution
from webweaver.studio.ui.framework.settings_page import (SettingsPage,
                                                         ValidationResult)


class BrowserSettingsPage(SettingsPage):

    def __init__(self, parent, context: StudioSolution):
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

        self._window_size_default = wx.RadioButton(
            scrolled, wx.ID_ANY, "Default size", style=wx.RB_GROUP)
        content.Add(self._window_size_default, 0, wx.ALL, 5)

        self._window_size_maximised = wx.RadioButton(
            scrolled, wx.ID_ANY, "Maximised (Recommended)")
        content.Add(self._window_size_maximised, 0, wx.ALL, 5)

        self._window_size_custom = wx.RadioButton(
            scrolled, wx.ID_ANY, "Custom size")
        content.Add(self._window_size_custom, 0, wx.ALL, 5)

        self._window_size_width = wx.TextCtrl(
            scrolled, wx.ID_ANY, "1280", size=(60, -1))
        self._window_size_height = wx.TextCtrl(
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
        self._advanced_user_agent = wx.TextCtrl(scrolled)
        content.Add(self._advanced_user_agent, 0, wx.EXPAND | wx.BOTTOM | wx.RIGHT, 12)

        '''


        self._behaviour_controls.window_size_maximised.SetValue(True)
        self._sync_window_size_state()

        self._behaviour_controls.window_size_maximised.Bind(
            wx.EVT_RADIOBUTTON, lambda evt: self._sync_window_size_state()
        )
        self._behaviour_controls.window_size_custom.Bind(
            wx.EVT_RADIOBUTTON, lambda evt: self._sync_window_size_state()
        )

        # Advanced section
        advanced_pane = wx.CollapsiblePane(self,  wx.ID_ANY, "Advanced")
        pane: wx.Window = advanced_pane.GetPane()

        adv_sizer: wx.BoxSizer = wx.BoxSizer(wx.VERTICAL)
        adv_sizer.Add(wx.StaticText(pane,
                                    wx.ID_ANY,
                                    "User agent override"),
                      0, wx.BOTTOM, 5)
        self._behaviour_controls.user_agent = wx.TextCtrl(pane,  wx.ID_ANY)
        adv_sizer.Add(self._behaviour_controls.user_agent, 0, wx.EXPAND)

        pane.SetSizer(adv_sizer)
        behaviour_box.Add(advanced_pane, 0, wx.EXPAND | wx.ALL, 5)


        '''

        # ---- Final wiring ----

        scrolled.SetSizer(content)
        scrolled.SetupScrolling(scroll_x=False)

        self.SetSizer(outer)

    def load(self):
        # self._start_max_checkbox.SetValue(self._settings.start_maximised)
        pass

    def validate(self) -> ValidationResult:
        pass

    def apply(self):
        pass
