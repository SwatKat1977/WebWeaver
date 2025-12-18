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
#include "ProjectCreateWizard/WizardFinishPage.h"
#include "WizardStepIndicator.h"
#include "ProjectWizardControlIDs.h"

namespace webweaver::studio {

WizardFinishPage::WizardFinishPage(wxWindow* parent,
                                   ProjectCreateWizardData* data,
                                   StepsList steps) :
    wxDialog(parent,
             wxID_ANY,
             "Set up your web test",
             wxDefaultPosition,
             wxDefaultSize,
             wxDEFAULT_DIALOG_STYLE),
    data_(data), steps_(steps) {
    wxBoxSizer *mainSizer = new wxBoxSizer(wxVERTICAL);

    WizardStepIndicator* stepIndicator = new WizardStepIndicator(this,
                                                                 steps_,
                                                                 3);
    mainSizer->Add(stepIndicator, 0, wxEXPAND | wxALL, 10);

    // Header
    wxBoxSizer *headerSizer = new wxBoxSizer(wxHORIZONTAL);
    wxStaticBitmap *icon = new wxStaticBitmap(
        this,
        wxID_ANY,
        wxArtProvider::GetBitmap(
        wxART_TIP, wxART_OTHER, wxSize(32, 32)));
    headerSizer->Add(icon, 0, wxALL, 10);

    wxBoxSizer *textSizer = new wxBoxSizer(wxVERTICAL);
    wxStaticText *title = new wxStaticText(this, wxID_ANY, "Almost there");
    title->SetFont(wxFont(13, wxFONTFAMILY_DEFAULT,
        wxFONTSTYLE_NORMAL, wxFONTWEIGHT_BOLD));
    wxStaticText *subtitle = new wxStaticText(
        this,
        wxID_ANY,
        "Read what's next and then click Finish to create "
        "your solution and get started.");
    subtitle->SetForegroundColour(wxColour(100, 100, 100));
    textSizer->Add(title, 0);
    textSizer->Add(subtitle, 0, wxTOP, 4);

    headerSizer->Add(textSizer, 1, wxALIGN_CENTER_VERTICAL);
    mainSizer->Add(headerSizer, 0, wxLEFT | wxRIGHT, 10);

    // Button bar
    wxBoxSizer *buttonBarSizer = new wxBoxSizer(wxHORIZONTAL);
    buttonBarSizer->AddStretchSpacer();

    wxButton *btnCancel = new wxButton(this, wxID_CANCEL, "Cancel");
    btnCancel->Bind(wxEVT_BUTTON,
        [this](wxCommandEvent&) { EndModal(wxID_CANCEL); });
    buttonBarSizer->Add(btnCancel, 0, wxRIGHT, 10);

    wxButton *btnBack = new wxButton(this,
                                     PROJECT_WIZARD_BACK_BUTTON_ID,
                                     "Back");
    btnBack->Bind(wxEVT_BUTTON,
        [this](wxCommandEvent&) {
            EndModal(PROJECT_WIZARD_BACK_BUTTON_ID); });
    buttonBarSizer->Add(btnBack, 0, wxRIGHT, 10);

    wxButton *btnNext = new wxButton(this, wxID_OK, "Finish");
    btnNext->Bind(wxEVT_BUTTON, &WizardFinishPage::OnNextClickEvent, this);
    buttonBarSizer->Add(btnNext, 0);

    mainSizer->Add(buttonBarSizer, 0, wxEXPAND | wxALL, 10);

    SetSizerAndFit(mainSizer);
    CentreOnParent();
}

void WizardFinishPage::OnNextClickEvent(wxCommandEvent& event) {
    EndModal(wxID_OK);
}

}   // namespace webweaver::studio
