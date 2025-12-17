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
#include "ProjectCreateWizard/WizardBehaviourPage.h"
#include "WizardStepIndicator.h"
#include "ProjectCreateWizard/BrowserIcons.h"
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
                                                                 3);
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

void WizardBehaviourPage::OnNextClickEvent(wxCommandEvent& event) {
    EndModal(wxID_OK);
}

}   // namespace webweaver::studio
