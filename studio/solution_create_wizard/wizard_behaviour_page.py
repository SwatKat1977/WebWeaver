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
import typing
import wx
from wizard_step_indicator import WizardStepIndicator
from solution_create_wizard.solution_create_wizard_data import \
    SolutionCreateWizardData
from solution_create_wizard.solution_widget_ids import \
    SOLUTION_WIZARD_BACK_BUTTON_ID
from solution_create_wizard.solution_creation_page import SolutionCreationPage


class WizardBehaviourPage(wx.Dialog):
    NEXT_WIZARD_PAGE = SolutionCreationPage.PAGE_NO_FINISH_PAGE

    def __init__(self, parent, data: SolutionCreateWizardData, steps: list):
        super().__init__(parent, title="Create your solution",
                         style=wx.DEFAULT_DIALOG_STYLE)
        self._data = data
        self._steps: list = list(steps)

        main_sizer: wx.BoxSizer = wx.BoxSizer(wx.VERTICAL)

        step_indicator = WizardStepIndicator(self, self._steps, 2)
        main_sizer.Add(step_indicator, 0, wx.EXPAND | wx.ALL, 10)

        # Recording behaviour controls
        self._chk_private: typing.Optional[wx.CheckBox] =  None
        self._chk_disable_extensions: typing.Optional[wx.CheckBox] =  None
        self._chk_disable_notifications: typing.Optional[wx.CheckBox] =  None
        self._chk_ignore_cert_errors: typing.Optional[wx.CheckBox] =  None

        self._radio_default_window_size: typing.Optional[wx.RadioButton] =  None
        self._radio_maximised: typing.Optional[wx.RadioButton] =  None
        self._radio_custom_window_size: typing.Optional[wx.RadioButton] =  None
        self._txt_window_width: typing.Optional[wx.TextCtrl] =  None
        self._txt_window_height: typing.Optional[wx.TextCtrl] =  None

        self._advanced_pane: typing.Optional[wx.CollapsiblePane] =  None
        self._txt_user_agent: typing.Optional[wx.wxTextCtrl] =  None

        # Header
        header_sizer: wx.BoxSizer = wx.BoxSizer(wx.HORIZONTAL)
        icon = wx.StaticBitmap(
            self,
            wx.ID_ANY,
            wx.ArtProvider.GetBitmap(wx.ART_TIP,
                                     wx.ART_OTHER,
                                     wx.Size(32, 32)))
        header_sizer.Add(icon, 0, wx.ALL, 10)

        text_box_sizer = wx.BoxSizer(wx.VERTICAL)
        title = wx.StaticText(self,
                              wx.ID_ANY,
                              "Set up automation behaviour")
        title.SetFont(wx.Font(13,
                              wx.FONTFAMILY_DEFAULT,
                              wx.FONTSTYLE_NORMAL,
                              wx.FONTWEIGHT_BOLD))
        subtitle = wx.StaticText(self,
                                 wx.ID_ANY,
                                 "How should the automation recording behave?")
        subtitle.SetForegroundColour(wx.Colour(100, 100, 100))
        text_box_sizer.Add(title, 0)
        text_box_sizer.Add(subtitle, 0, wx.TOP, 4)

        header_sizer.Add(text_box_sizer, 1, wx.ALIGN_CENTER_VERTICAL)
        main_sizer.Add(header_sizer, 0, wx.LEFT | wx.RIGHT, 10)

        content_sizer = wx.BoxSizer(wx.VERTICAL)
        self._create_behaviour_panel(content_sizer)
        main_sizer.Add(content_sizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 20)

        # Button bar
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        button_sizer.AddStretchSpacer()

        btn_cancel = wx.Button(self, wx.ID_CANCEL, "Cancel")
        btn_cancel.Bind(wx.EVT_BUTTON, lambda evt: self.EndModal(wx.ID_CANCEL))
        button_sizer.Add(btn_cancel, 0, wx.RIGHT, 10)

        btn_back = wx.Button(self,
                             SOLUTION_WIZARD_BACK_BUTTON_ID,
                             "Back")
        btn_back.Bind(wx.EVT_BUTTON,
                      lambda evt: self.EndModal(SOLUTION_WIZARD_BACK_BUTTON_ID))
        button_sizer.Add(btn_back, 0, wx.RIGHT, 10)

        btn_next = wx.Button(self, wx.ID_OK, "Next")
        ##btn_next.Bind(wx.EVT_BUTTON, self._on_next_click_event)
        button_sizer.Add(btn_next, 0)

        main_sizer.Add(button_sizer, 0, wx.EXPAND | wx.ALL, 10)

        self.SetSizerAndFit(main_sizer)
        self.CentreOnParent()

    def _create_behaviour_panel(self, parent: wx.BoxSizer) -> None:
        behaviour_box = wx.StaticBoxSizer(wx.VERTICAL,
                                          self,
                                          "Recording Browser Settings")

        self._chk_private = wx.CheckBox(
            self,
            wx.ID_ANY,
            "Private / Incognito mode (recommended)")
        self._chk_disable_extensions = wx.CheckBox(
            self,
            wx.ID_ANY,
            "Disable extensions (recommended)")
        self._chk_disable_notifications = wx.CheckBox(
            self,
            wx.ID_ANY,
            "Disable notifications (recommended)")
        self._chk_ignore_cert_errors = wx.CheckBox(
            self,
            wx.ID_ANY,
            "Ignore certificate errors (advanced)")

        self._chk_private.SetValue(True)
        self._chk_disable_extensions.SetValue(True)
        self._chk_disable_notifications.SetValue(True)

        behaviour_box.Add(self._chk_private, 0, wx.ALL, 5)
        behaviour_box.Add(self._chk_disable_extensions, 0, wx.ALL, 5)
        behaviour_box.Add(self._chk_disable_notifications, 0, wx.ALL, 5)
        behaviour_box.Add(self._chk_ignore_cert_errors, 0, wx.ALL, 5)

        behaviour_box.AddSpacer(10)

        # Window size section
        window_label = wx.StaticText(self,  wx.ID_ANY, "Browser window")
        window_label.SetFont(window_label.GetFont().Bold())

        behaviour_box.Add(window_label, 0, wx.ALL, 5)

        """
        # Recording behaviour controls
        self._chk_private: typing.Optional[wx.CheckBox] =  None
        self._chk_disable_extensions: typing.Optional[wx.CheckBox] =  None
        self._chk_disable_notifications: typing.Optional[wx.CheckBox] =  None
        self._chk_ignore_cert_errors: typing.Optional[wx.CheckBox] =  None

        self._radio_default_window_size: typing.Optional[wx.RadioButton] =  None
        self._radio_maximised: typing.Optional[wx.RadioButton] =  None
        self._radio_custom_window_size: typing.Optional[wx.RadioButton] =  None
        self._txt_window_width: typing.Optional[wx.TextCtrl] =  None
        self._txt_window_height: typing.Optional[wx.TextCtrl] =  None

        self._advanced_pane: typing.Optional[wx.CollapsiblePane] =  None
        self._txt_user_agent: typing.Optional[wx.wxTextCtrl] =  None
        """

        self._radio_default_window_size = wx.RadioButton(self,
                                                         wx.ID_ANY,
                                                         "Default size",
                                                         style=wx.RB_GROUP)
        self._radio_maximised = wx.RadioButton(self,
                                               wx.ID_ANY,
                                               "Maximised (Recommended)")
        self._radio_custom_window_size = wx.RadioButton(self,
                                                        wx.ID_ANY,
                                                        "Custom size")

        self._txt_window_width = wx.TextCtrl(self,
                                             wx.ID_ANY,
                                             "1280",
                                             size=(60, -1))
        self._txt_window_height = wx.TextCtrl(self,
                                              wx.ID_ANY,
                                              "800",
                                              size=(60, -1))

        size_sizer: wx.BoxSizer = wx.BoxSizer(wx.HORIZONTAL)
        size_sizer.Add(self._txt_window_width, 0, wx.RIGHT, 5)
        size_sizer.Add(wx.StaticText(self,  wx.ID_ANY, "×"),
                       0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        size_sizer.Add(self._txt_window_height, 0)

        behaviour_box.Add(self._radio_default_window_size, 0, wx.ALL, 5)
        behaviour_box.Add(self._radio_maximised, 0, wx.ALL, 5)
        behaviour_box.Add(self._radio_custom_window_size,
                          0,
                          wx.LEFT | wx.TOP,
                          5)
        behaviour_box.Add(size_sizer, 0, wx.LEFT | wx.BOTTOM, 10)

        self._radio_maximised.SetValue(True)
        ####self._sync_window_size_state()

        """
        self._radio_maximised.Bind(wxEVT_RADIOBUTTON,
                               [this](wxCommandEvent&) { SyncWindowSizeState(); })
        self._radio_custom_window_size.Bind(wxEVT_RADIOBUTTON,
                                [this](wxCommandEvent&) { SyncWindowSizeState(); })
        """

        # Advanced section
        self._advanced_pane = wx.CollapsiblePane(self,  wx.ID_ANY, "Advanced")
        pane: wx.Window = self._advanced_pane.GetPane()

        adv_sizer: wx.BoxSizer = wx.BoxSizer(wx.VERTICAL)
        adv_sizer.Add(wx.StaticText(pane,
                                    wx.ID_ANY,
                                    "User agent override"),
                      0, wx.BOTTOM, 5)
        self._txt_user_agent = wx.TextCtrl(pane,  wx.ID_ANY)
        adv_sizer.Add(self._txt_user_agent, 0, wx.EXPAND)

        pane.SetSizer(adv_sizer)
        behaviour_box.Add(self._advanced_pane, 0, wx.EXPAND | wx.ALL, 5)

        parent.Add(behaviour_box, 1, wx.EXPAND)

"""
 private:

    def _on_next_click_event(event: wxCommandEvent&) . None:
        auto& opts = data_.browserLaunchOptions;

        opts.privateMode = chkPrivate_.GetValue();
        opts.disableExtensions = chkDisableExtensions_.GetValue();
        opts.disableNotifications = chkDisableNotifications_.GetValue();
        opts.ignoreCertificateErrors = chkIgnoreCertErrors_.GetValue();

        opts.maximised = radioMaximised_.GetValue();
        bool customWindowSize = radioCustomWindowSize_.GetValue();
        bool defaultWindowSize = radioDefaultWindowSize_.GetValue();

        if (opts.maximised) {
            opts.windowSize.reset();
        } else if (defaultWindowSize) {
            opts.maximised = false;
            opts.windowSize.reset();
        } else {
            opts.windowSize = WindowSize{
                static_cast<uint32_t>(wxAtoi(self._txt_window_width.GetValue())),
                static_cast<uint32_t>(wxAtoi(txtWindowHeight_.GetValue()))
            };
            opts.maximised = false;
        }

        const wxString userAgent = txtUserAgent_.GetValue();
        if (!userAgent.IsEmpty()) {
            opts.userAgent = userAgent.ToStdString();
        } else {
            opts.userAgent.reset();
        }

        EndModal(wxID_OK);
    }



    void CreateBehaviourPanel(wxBoxSizer* parent);
    void SyncWindowSizeState();
};




#include <wx/artprov.h>

void WizardBehaviourPage::SyncWindowSizeState() {
    bool custom = radioCustomWindowSize_.GetValue();
    self._txt_window_width.Enable(custom);
    txtWindowHeight_.Enable(custom);
}
"""
