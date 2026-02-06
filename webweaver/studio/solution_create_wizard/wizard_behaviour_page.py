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
from dataclasses import dataclass
import wx
from ..browser_launch_options import BrowserLaunchOptions, WindowSize
from ..solution_create_wizard.solution_create_wizard_data import \
    SolutionCreateWizardData
from ..solution_create_wizard.solution_creation_page import SolutionCreationPage
from ..solution_create_wizard.solution_wizard_base import SolutionWizardBase


@dataclass
class BehaviourPageControls:
    """
    Container for all UI controls on the wizard "Behaviour" configuration page.

    This dataclass groups together references to all wxPython widgets used to
    configure browser launch and recording behaviour, including:

    - Basic behaviour options (privacy, extensions, notifications, certificates)
    - Browser window sizing options (default, maximised, or custom size)
    - Advanced options (user agent override)

    The class does not contain any logic itself; it simply serves as a structured
    holder for the UI elements so they can be accessed, validated, and read
    consistently from the wizard page implementation.
    """
    # pylint: disable=too-many-instance-attributes

    # Basic behaviour
    private: wx.CheckBox | None = None
    disable_extensions: wx.CheckBox | None = None
    disable_notifications: wx.CheckBox | None = None
    ignore_cert_errors: wx.CheckBox | None = None
    disable_automation_controlled_feature: wx.CheckBox | None = None

    # Window Size behaviour
    window_size_default: wx.RadioButton | None = None
    window_size_maximised: wx.RadioButton | None = None
    window_size_custom: wx.RadioButton | None = None
    window_size_width: wx.TextCtrl | None = None
    window_size_height: wx.TextCtrl | None = None

    # Advanced behaviour
    user_agent: wx.TextCtrl | None = None


class WizardBehaviourPage(SolutionWizardBase):
    """
    Wizard page for configuring browser and recording behaviour.

    This page allows the user to configure how the automation browser will be
    launched and how recording should behave, including:

    - Private / incognito mode
    - Disabling extensions and notifications
    - Certificate error handling
    - Browser window sizing behaviour (default, maximised, or custom size)
    - Optional user agent override

    The selected options are written back into the shared
    SolutionCreateWizardData object when the user proceeds to the next step.
    """
    # pylint: disable=too-few-public-methods

    NEXT_WIZARD_PAGE = SolutionCreationPage.PAGE_NO_FINISH_PAGE

    TITLE_STR: str = "Set up automation behaviour"
    SUBTITLE_STR: str = "How should the automation recording behave?"

    def __init__(self, parent, data: SolutionCreateWizardData):
        super().__init__("Finalisation your solution",
                         parent, data, 2)

        # Recording behaviour controls
        self._behaviour_controls = BehaviourPageControls()

        # Header
        self._create_header(self.TITLE_STR, self.SUBTITLE_STR)

        # Wizard contents
        content_sizer = wx.BoxSizer(wx.VERTICAL)
        self._create_behaviour_panel(content_sizer)
        self._main_sizer.Add(content_sizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 20)

        # Button bar
        self._create_buttons_bar(self._on_next_click_event)

        self.SetSizerAndFit(self._main_sizer)
        self.CentreOnParent()

    def _create_behaviour_panel(self, parent: wx.BoxSizer) -> None:
        behaviour_box = wx.StaticBoxSizer(wx.VERTICAL,
                                          self,
                                          "Recording Browser Settings")
        # =================
        # = Basic behaviour
        # =================
        self._behaviour_controls.private = wx.CheckBox(
            self, wx.ID_ANY, "Private / Incognito mode (recommended)")
        self._behaviour_controls.disable_extensions = wx.CheckBox(
            self, wx.ID_ANY, "Disable extensions (recommended)")
        self._behaviour_controls.disable_notifications = wx.CheckBox(
            self, wx.ID_ANY, "Disable notifications (recommended)")
        self._behaviour_controls.ignore_cert_errors = wx.CheckBox(
            self, wx.ID_ANY, "Ignore certificate errors (advanced)")
        self._behaviour_controls.disable_automation_controlled_feature = \
            wx.CheckBox(self,
                        wx.ID_ANY,
                        "Disable Automation Controlled Feature (advanced)")

        self._behaviour_controls.private.SetValue(True)
        self._behaviour_controls.disable_extensions.SetValue(True)
        self._behaviour_controls.disable_notifications.SetValue(True)
        behaviour_box.Add(self._behaviour_controls.private, 0, wx.ALL, 5)
        behaviour_box.Add(self._behaviour_controls.disable_extensions,
                          0, wx.ALL, 5)
        behaviour_box.Add(self._behaviour_controls.disable_notifications,
                          0, wx.ALL, 5)
        behaviour_box.Add(self._behaviour_controls.ignore_cert_errors,
                          0, wx.ALL, 5)
        behaviour_box.Add(
            self._behaviour_controls.disable_automation_controlled_feature,
            0, wx.ALL, 5)

        behaviour_box.AddSpacer(10)

        # =====================
        # = Window size section
        # =====================
        window_label = wx.StaticText(self,  wx.ID_ANY, "Browser window")
        window_label.SetFont(window_label.GetFont().Bold())
        behaviour_box.Add(window_label, 0, wx.ALL, 5)
        self._behaviour_controls.window_size_default = wx.RadioButton(
            self, wx.ID_ANY, "Default size", style=wx.RB_GROUP)
        self._behaviour_controls.window_size_maximised = wx.RadioButton(
            self, wx.ID_ANY, "Maximised (Recommended)")
        self._behaviour_controls.window_size_custom = wx.RadioButton(
            self, wx.ID_ANY, "Custom size")
        self._behaviour_controls.window_size_width = wx.TextCtrl(
            self, wx.ID_ANY, "1280", size=(60, -1))
        self._behaviour_controls.window_size_height = wx.TextCtrl(
            self, wx.ID_ANY, "800", size=(60, -1))

        size_sizer: wx.BoxSizer = wx.BoxSizer(wx.HORIZONTAL)
        size_sizer.Add(self._behaviour_controls.window_size_width,
                       0, wx.RIGHT, 5)
        size_sizer.Add(wx.StaticText(self,  wx.ID_ANY, "×"),
                       0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        size_sizer.Add(self._behaviour_controls.window_size_height, 0)
        behaviour_box.Add(self._behaviour_controls.window_size_default,
                          0, wx.ALL, 5)
        behaviour_box.Add(self._behaviour_controls.window_size_maximised,
                          0, wx.ALL, 5)
        behaviour_box.Add(self._behaviour_controls.window_size_custom,
                          0, wx.LEFT | wx.TOP, 5)
        behaviour_box.Add(size_sizer, 0, wx.LEFT | wx.BOTTOM, 10)

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

        parent.Add(behaviour_box, 1, wx.EXPAND)

    def _sync_window_size_state(self) -> None:
        custom: bool = self._behaviour_controls.window_size_custom.GetValue()
        self._behaviour_controls.window_size_width.Enable(custom)
        self._behaviour_controls.window_size_height.Enable(custom)

    def _on_next_click_event(self, _event: wx.CommandEvent) -> None:
        opts: BrowserLaunchOptions = self._data.browser_launch_options

        opts.private_mode = self._behaviour_controls.private.GetValue()
        opts.disable_extensions = \
            self._behaviour_controls.disable_extensions.GetValue()
        opts.disable_notifications = \
            self._behaviour_controls.disable_notifications.GetValue()
        opts.ignore_certificate_errors = \
            self._behaviour_controls.ignore_cert_errors.GetValue()
        opts.disable_automation_controlled_feature = \
            self._behaviour_controls.disable_automation_controlled_feature.GetValue()

        opts.maximised = \
            self._behaviour_controls.window_size_maximised.GetValue()
        default_window_size: bool = \
            self._behaviour_controls.window_size_default.GetValue()

        if opts.maximised:
            opts.window_size = None

        elif default_window_size:
            opts.maximised = False
            opts.window_size = None

        else:
            # Custom window size
            try:
                width = \
                    int(self._behaviour_controls.window_size_width.GetValue())
                height = \
                    int(self._behaviour_controls.window_size_height.GetValue())
            except ValueError:
                wx.MessageBox("Please enter valid numeric window dimensions.",
                              "Invalid input", wx.ICON_WARNING)
                return

            opts.window_size = WindowSize(width=width, height=height)
            opts.maximised = False

        user_agent: str = self._behaviour_controls.user_agent.GetValue().strip()
        if user_agent:
            opts.user_agent = user_agent

        else:
            opts.user_agent = None

        self.EndModal(wx.ID_OK)
