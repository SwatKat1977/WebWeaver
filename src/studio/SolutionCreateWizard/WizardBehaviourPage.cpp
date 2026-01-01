/*
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
*/
#include <wx/artprov.h>
#include "SolutionCreateWizard/WizardBehaviourPage.h"
#include "WizardStepIndicator.h"
#include "SolutionCreateWizard/BrowserIcons.h"
#include "ProjectWizardControlIDs.h"


namespace webweaver::studio {

WizardBehaviourPage::WizardBehaviourPage(wxWindow* parent,
                                         ProjectCreateWizardData* data,
                                         StepsList steps) :
    wxDialog(parent,
             wxID_ANY,
             "Create your new solution",
             wxDefaultPosition,
             wxDefaultSize,
             wxDEFAULT_DIALOG_STYLE), data_(data), steps_(steps) {
    wxBoxSizer* mainSizer = new wxBoxSizer(wxVERTICAL);

    WizardStepIndicator* stepIndicator = new WizardStepIndicator(this,
                                                                 steps_,
                                                                 2);
    mainSizer->Add(stepIndicator, 0, wxEXPAND | wxALL, 10);

    // Header
    wxBoxSizer *headerSizer = new wxBoxSizer(wxHORIZONTAL);
    wxStaticBitmap *icon = new wxStaticBitmap(
        this,
        wxID_ANY,
        wxArtProvider::GetBitmap(wxART_TIP,
                                 wxART_OTHER,
                                 wxSize(32, 32)));
    headerSizer->Add(icon, 0, wxALL, 10);

    wxBoxSizer *textBoxSizer = new wxBoxSizer(wxVERTICAL);
    wxStaticText *title = new wxStaticText(this,
                                           wxID_ANY,
                                           "Set up automation behaviour");
    title->SetFont(wxFont(13,
                          wxFONTFAMILY_DEFAULT,
                          wxFONTSTYLE_NORMAL,
                          wxFONTWEIGHT_BOLD));
    wxStaticText *subtitle = new wxStaticText(
        this, wxID_ANY, "How should the automation recording behave?");
    subtitle->SetForegroundColour(wxColour(100, 100, 100));
    textBoxSizer->Add(title, 0);
    textBoxSizer->Add(subtitle, 0, wxTOP, 4);

    headerSizer->Add(textBoxSizer, 1, wxALIGN_CENTER_VERTICAL);
    mainSizer->Add(headerSizer, 0, wxLEFT | wxRIGHT, 10);

    wxBoxSizer* contentSizer = new wxBoxSizer(wxVERTICAL);
    CreateBehaviourPanel(contentSizer);
    mainSizer->Add(contentSizer, 0, wxEXPAND | wxLEFT | wxRIGHT, 20);

    // Button bar
    wxBoxSizer *buttonSizer = new wxBoxSizer(wxHORIZONTAL);
    buttonSizer->AddStretchSpacer();

    wxButton *btnCancel = new wxButton(this, wxID_CANCEL, "Cancel");
    btnCancel->Bind(wxEVT_BUTTON,
                    [this](wxCommandEvent&) { EndModal(wxID_CANCEL); });
    buttonSizer->Add(btnCancel, 0, wxRIGHT, 10);

    wxButton *btnBack = new wxButton(this,
                                     PROJECT_WIZARD_BACK_BUTTON_ID,
                                     "Back");
    btnBack->Bind(wxEVT_BUTTON,
                  [this](wxCommandEvent&) {
            EndModal(PROJECT_WIZARD_BACK_BUTTON_ID); });
    buttonSizer->Add(btnBack, 0, wxRIGHT, 10);

    wxButton *btnNext = new wxButton(this, wxID_OK, "Next");
    btnNext->Bind(wxEVT_BUTTON, &WizardBehaviourPage::OnNextClickEvent, this);
    buttonSizer->Add(btnNext, 0);

    mainSizer->Add(buttonSizer, 0, wxEXPAND | wxALL, 10);

    SetSizerAndFit(mainSizer);
    CentreOnParent();
}

void WizardBehaviourPage::OnNextClickEvent(wxCommandEvent&)
{
    auto& opts = data_->browserLaunchOptions;

    opts.privateMode = chkPrivate_->GetValue();
    opts.disableExtensions = chkDisableExtensions_->GetValue();
    opts.disableNotifications = chkDisableNotifications_->GetValue();
    opts.ignoreCertificateErrors = chkIgnoreCertErrors_->GetValue();

    opts.maximised = radioMaximised_->GetValue();
    bool customWindowSize = radioCustomWindowSize_->GetValue();
    bool defaultWindowSize = radioDefaultWindowSize_->GetValue();

    if (opts.maximised) {
        opts.windowSize.reset();  
    } else if (defaultWindowSize) {
        opts.maximised = false;
        opts.windowSize.reset();
    } else {
        opts.windowSize = WindowSize{
            static_cast<uint32_t>(wxAtoi(txtWindowWidth_->GetValue())),
            static_cast<uint32_t>(wxAtoi(txtWindowHeight_->GetValue()))
        };  
        opts.maximised = false;  
    }

    const wxString userAgent = txtUserAgent_->GetValue();
    if (!userAgent.IsEmpty()) {
        opts.userAgent = userAgent.ToStdString();
    } else {
        opts.userAgent.reset();
    }

    EndModal(wxID_OK);
}

void WizardBehaviourPage::CreateBehaviourPanel(wxBoxSizer* parent)
{
    wxStaticBoxSizer* behaviourBox =
        new wxStaticBoxSizer(wxVERTICAL, this, "Recording Browser Settings");

    chkPrivate_ = new wxCheckBox(this, wxID_ANY,
                                 "Private / Incognito mode (recommended)");
    chkDisableExtensions_ = new wxCheckBox(this, wxID_ANY,
                                           "Disable extensions (recommended)");
    chkDisableNotifications_ = new wxCheckBox(this, wxID_ANY,
                                              "Disable notifications (recommended)");
    chkIgnoreCertErrors_ = new wxCheckBox(this, wxID_ANY,
                                          "Ignore certificate errors (advanced)");

    chkPrivate_->SetValue(true);
    chkDisableExtensions_->SetValue(true);
    chkDisableNotifications_->SetValue(true);

    behaviourBox->Add(chkPrivate_, 0, wxALL, 5);
    behaviourBox->Add(chkDisableExtensions_, 0, wxALL, 5);
    behaviourBox->Add(chkDisableNotifications_, 0, wxALL, 5);
    behaviourBox->Add(chkIgnoreCertErrors_, 0, wxALL, 5);

    behaviourBox->AddSpacer(10);

    // Window size section
    wxStaticText* windowLabel =
        new wxStaticText(this, wxID_ANY, "Browser window");
    windowLabel->SetFont(windowLabel->GetFont().Bold());

    behaviourBox->Add(windowLabel, 0, wxALL, 5);

    radioDefaultWindowSize_ = new wxRadioButton(this, wxID_ANY,
                                        "Defeault size",
                                        wxDefaultPosition,
                                        wxDefaultSize,
                                        wxRB_GROUP);
    radioMaximised_ = new wxRadioButton(this, wxID_ANY,
                                        "Maximised (Recommended)",
                                        wxDefaultPosition,
                                        wxDefaultSize);
    radioCustomWindowSize_ = new wxRadioButton(this, wxID_ANY,
                                               "Custom size");

    txtWindowWidth_ = new wxTextCtrl(this, wxID_ANY, "1280",
                                    wxDefaultPosition, wxSize(60, -1));
    txtWindowHeight_ = new wxTextCtrl(this, wxID_ANY, "800",
                                      wxDefaultPosition, wxSize(60, -1));

    wxBoxSizer* sizeSizer = new wxBoxSizer(wxHORIZONTAL);
    sizeSizer->Add(txtWindowWidth_, 0, wxRIGHT, 5);
    sizeSizer->Add(new wxStaticText(this, wxID_ANY, "×"),
                   0, wxALIGN_CENTER_VERTICAL | wxRIGHT, 5);
    sizeSizer->Add(txtWindowHeight_, 0);

    behaviourBox->Add(radioDefaultWindowSize_, 0, wxALL, 5);
    behaviourBox->Add(radioMaximised_, 0, wxALL, 5);
    behaviourBox->Add(radioCustomWindowSize_, 0, wxLEFT | wxTOP, 5);
    behaviourBox->Add(sizeSizer, 0, wxLEFT | wxBOTTOM, 10);

    radioMaximised_->SetValue(true);
    SyncWindowSizeState();

    radioMaximised_->Bind(wxEVT_RADIOBUTTON,
                           [this](wxCommandEvent&) { SyncWindowSizeState(); });
    radioCustomWindowSize_->Bind(wxEVT_RADIOBUTTON,
                            [this](wxCommandEvent&) { SyncWindowSizeState(); });

    // Advanced section
    advancedPane_ = new wxCollapsiblePane(this, wxID_ANY, "Advanced");
    wxWindow* pane = advancedPane_->GetPane();

    wxBoxSizer* advSizer = new wxBoxSizer(wxVERTICAL);
    advSizer->Add(new wxStaticText(pane, wxID_ANY, "User agent override"), 0, wxBOTTOM, 5);
    txtUserAgent_ = new wxTextCtrl(pane, wxID_ANY);
    advSizer->Add(txtUserAgent_, 0, wxEXPAND);

    pane->SetSizer(advSizer);
    behaviourBox->Add(advancedPane_, 0, wxEXPAND | wxALL, 5);

    parent->Add(behaviourBox, 1, wxEXPAND);
}

void WizardBehaviourPage::SyncWindowSizeState()
{
    bool custom = radioCustomWindowSize_->GetValue();
    txtWindowWidth_->Enable(custom);
    txtWindowHeight_->Enable(custom);
}

}   // namespace webweaver::studio
