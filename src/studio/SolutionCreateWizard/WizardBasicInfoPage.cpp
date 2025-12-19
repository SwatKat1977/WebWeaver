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
#include <string>
#include <vector>
#include "SolutionCreateWizard/WizardBasicInfoPage.h"
#include "WizardStepIndicator.h"
#include "FilesystemUtils.h"


namespace webweaver::studio {

WizardBasicInfoPage::WizardBasicInfoPage(wxWindow* parent,
                                         ProjectCreateWizardData* data,
                                         std::vector<std::string> steps)
    : wxDialog(parent,
               wxID_ANY,
               "Create your new solution",
               wxDefaultPosition,
               wxDefaultSize,
               wxDEFAULT_DIALOG_STYLE), data_(data), steps_(steps) {
    wxBoxSizer *main = new wxBoxSizer(wxVERTICAL);

    WizardStepIndicator*stepIndicator = new WizardStepIndicator(this,
                                                                steps_,
                                                                0);
    main->Add(stepIndicator, 0, wxEXPAND | wxALL, 10);

    // --------------------------------------------------------------
    // Header
    // --------------------------------------------------------------
    wxBoxSizer *header = new wxBoxSizer(wxHORIZONTAL);
    wxStaticBitmap *icon = new wxStaticBitmap(
        this,
        wxID_ANY,
        wxArtProvider::GetBitmap(wxART_TIP, wxART_OTHER, wxSize(32, 32)));
    header->Add(icon, 0, wxALL, 10);

    // Text area (vertical sizer)
    wxBoxSizer *headerArea = new wxBoxSizer(wxVERTICAL);

    // Title
    wxStaticText* title = new wxStaticText(
        this,
        wxID_ANY,
        "Create your new solution");
    title->SetFont(wxFont(13, wxFONTFAMILY_DEFAULT,
        wxFONTSTYLE_NORMAL, wxFONTWEIGHT_BOLD));

    // Subtitle
    wxStaticText* subtitle = new wxStaticText(
        this,
        wxID_ANY,
        "Define basic information for your first solution.");
    subtitle->SetForegroundColour(wxColour(100, 100, 100));
    headerArea->Add(title, 0);
    headerArea->Add(subtitle, 0, wxTOP, 4);

    // Add text area into header sizer
    header->Add(headerArea, 1, wxALIGN_CENTER_VERTICAL);

    // Add the whole header to main sizer
    main->Add(header, 0, wxLEFT | wxRIGHT, 10);

    // --------------------------------------------------------------
    // Input Area
    // --------------------------------------------------------------

    wxPanel* inputAreaPanel = new wxPanel(this);
    wxFlexGridSizer *inputAreaSizer = new wxFlexGridSizer(0, 3, 8, 8);
    inputAreaSizer->AddGrowableCol(1, 1);

    // -----
    // Row 1 : Solution name
    // -----
    inputAreaSizer->Add(new wxStaticText(inputAreaPanel,
                                         wxID_ANY,
                                         "Solution name:"),
                        0, wxALIGN_CENTER_VERTICAL);
    txtSolutionName_ = new wxTextCtrl(inputAreaPanel, wxID_ANY);
    inputAreaSizer->Add(txtSolutionName_, 1, wxEXPAND);
    inputAreaSizer->AddSpacer(0);

    // -----
    // Row 2 : Solution location
    // -----
    inputAreaSizer->Add(new wxStaticText(inputAreaPanel,
                                         wxID_ANY,
                                         "Location:"),
                                         0, wxALIGN_CENTER_VERTICAL);
    txtSolutionDir_ = new wxTextCtrl(inputAreaPanel, wxID_ANY);
    inputAreaSizer->Add(txtSolutionDir_, 1, wxEXPAND);

    wxButton *btnBrowseLocation = new wxButton(inputAreaPanel,
                                               wxID_ANY,
                                               wxString::FromUTF8("…"));
    btnBrowseLocation->SetMinSize(wxSize(32, -1));
    btnBrowseLocation->Bind(wxEVT_BUTTON,
                            &WizardBasicInfoPage::OnBrowseSolutionLocation,
                            this);
    inputAreaSizer->Add(btnBrowseLocation, 0);

    inputAreaPanel->SetSizer(inputAreaSizer);
    main->Add(inputAreaPanel, 0, wxEXPAND | wxALL, 10);

    // -----
    // Row 3 : Create solution directory checkbox
    // -----
    chkCreateSolutionDir_ = new wxCheckBox(this,
                                           wxID_ANY,
                                           "Create directory for solution");
    chkCreateSolutionDir_->SetValue(true);
    main->Add(chkCreateSolutionDir_, 0, wxLEFT | wxRIGHT | wxBOTTOM, 10);

    // -----
    // Row 4 : Button bar
    // -----
    wxBoxSizer* btnButtonBarSizer = new wxBoxSizer(wxHORIZONTAL);
    // Spacer to push buttons to the right
    btnButtonBarSizer->AddStretchSpacer();

    // Cancel button
    wxButton *btnCancel = new wxButton(this, wxID_CANCEL, "Cancel");
    btnCancel->Bind(wxEVT_BUTTON,
                    [this](wxCommandEvent&) { EndModal(wxID_CANCEL); });
    btnButtonBarSizer->Add(btnCancel, 0, wxRIGHT, 10);

    // Next button
    wxButton *btnNext = new wxButton(this, wxID_OK, "Next");
    btnNext->Bind(wxEVT_BUTTON,
                  &WizardBasicInfoPage::OnNextClickEvent,
                  this);
    btnButtonBarSizer->Add(btnNext, 0);

    // Add to main layout
    main->Add(btnButtonBarSizer, 0, wxEXPAND | wxALL, 10);

    SetSizerAndFit(main);
    CentreOnParent();
}

void WizardBasicInfoPage::OnBrowseSolutionLocation(wxCommandEvent& event) {
    wxDirDialog dlg = wxDirDialog(this, "Choose solution location");
    if (dlg.ShowModal() == wxID_OK) {
        txtSolutionDir_->SetValue(dlg.GetPath());
    }
}


bool WizardBasicInfoPage::ValidateFields() {
    wxString SolutionName = txtSolutionName_->GetValue().Strip(wxString::both);
    if (SolutionName.IsEmpty()) {
        wxMessageBox("Please enter a solution name.",
                     "Validation error",
                     wxICON_WARNING);
        return false;
    }

    wxString solutionDir = txtSolutionDir_->GetValue().Strip(wxString::both);
    if (solutionDir.IsEmpty()) {
        wxMessageBox("Please enter a solution location.",
                     "Validation error",
                     wxICON_WARNING);
        return false;
    }

    auto solutionDirStr = std::filesystem::path(solutionDir.ToStdString());

#if defined(WEBWEAVER_PLATFORM_WIN64)
    auto p = solutionDirStr.lexically_normal();

    if (p.root_name() == "C:" &&
        p.has_root_directory() &&
        p.root_path() == p) {
        wxMessageBox(
            "The root of the C: drive is not writable.\n"
            "Please choose a folder inside your Documents or AppData directory.",
            "Permission error",
            wxICON_WARNING
        );
        return false;
    }
#endif

    if (!isdDirectoryWritable(solutionDirStr)) {
        wxMessageBox("The specified solution location is not valid/writable."
                     " Please choose another location.",
                     "Validation error",
                     wxICON_WARNING);
        return false;
    }

    data_->solutionName = SolutionName.ToStdString();
    data_->solutionDirectory = solutionDir.ToStdString();
    data_->createSolutionDir = chkCreateSolutionDir_->GetValue();

    return true;
}

void WizardBasicInfoPage::OnNextClickEvent(wxCommandEvent& event) {
    if (!ValidateFields()) {
        return;
    }

    EndModal(wxID_OK);
}

}   // namespace webweaver::studio
