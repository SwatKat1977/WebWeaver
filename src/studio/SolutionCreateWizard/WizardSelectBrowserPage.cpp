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
#include <wx/wx.h>
#include <wx/artprov.h>
#include <string>
#include <utility>
#include <vector>
#include "WizardSelectBrowserPage.h"
#include "ProjectCreateWizard/BrowserIcons.h"
#include "WizardStepIndicator.h"
#include "ProjectWizardControlIDs.h"

namespace webweaver::studio {

WizardSelectBrowserPage::WizardSelectBrowserPage(wxWindow* parent,
                                                 ProjectCreateWizardData* data,
                                                 std::vector<std::string> steps)
    : wxDialog(parent,
        wxID_ANY,
        "Set up your web test",
        wxDefaultPosition,
        wxDefaultSize,
        wxDEFAULT_DIALOG_STYLE), data_(data), steps_(steps) {
    wxBoxSizer *mainSizer = new wxBoxSizer(wxVERTICAL);

    // --- Step indicator ---
    WizardStepIndicator* stepIndicator = new WizardStepIndicator(this,
                                                                 steps_,
                                                                 1);
    mainSizer->Add(stepIndicator, 0, wxEXPAND | wxALL, 10);

    // --- Header ---
    wxBoxSizer *headerSizer = new wxBoxSizer(wxHORIZONTAL);

    // --- Wizard page icon ---
    wxBitmap iconBitmap = wxArtProvider::GetBitmap(
        wxART_TIP, wxART_OTHER, wxSize(32, 32));
    wxStaticBitmap* icon = new wxStaticBitmap(this, wxID_ANY, iconBitmap);
    headerSizer->Add(icon, 0, wxALL, 10);

    wxBoxSizer *textBox = new wxBoxSizer(wxVERTICAL);
    wxStaticText *title = new wxStaticText(this,
                                           wxID_ANY,
                                           "Set up your web test");
    title->SetFont(wxFont(13, wxFONTFAMILY_DEFAULT,
        wxFONTSTYLE_NORMAL, wxFONTWEIGHT_BOLD));
    wxStaticText *subtitle = new wxStaticText(
        this, wxID_ANY, "Which web browser do you want to test on?");
    subtitle->SetForegroundColour(wxColour(100, 100, 100));
    textBox->Add(title, 0);
    textBox->Add(subtitle, 0, wxTOP, 4);

    headerSizer->Add(textBox, 1, wxALIGN_CENTER_VERTICAL);
    mainSizer->Add(headerSizer, 0, wxLEFT | wxRIGHT, 10);

    // URL
    wxBoxSizer *urlSizer = new wxBoxSizer(wxVERTICAL);
    urlSizer->Add(new wxStaticText(this, wxID_ANY, "URL"), 0, wxBOTTOM, 4);
    _txtBaseUrl = new wxTextCtrl(this, wxID_ANY, DEFAULT_URL);
    urlSizer->Add(_txtBaseUrl, 0, wxEXPAND);
    mainSizer->Add(urlSizer, 0, wxEXPAND | wxALL, 10);

    // Browser label + hint
    wxStaticText *lblBrowser = new wxStaticText(
        this, wxID_ANY, "Select browser");
    lblBrowser->SetFont(wxFont(10, wxFONTFAMILY_DEFAULT,
        wxFONTSTYLE_NORMAL, wxFONTWEIGHT_BOLD));
    mainSizer->Add(lblBrowser, 0, wxLEFT | wxRIGHT, 10);

    wxStaticText *hint = new wxStaticText(
        this, wxID_ANY,
        "The selected browser must be installed on this system.");
    hint->SetForegroundColour(wxColour(120, 120, 120));
    mainSizer->Add(hint, 0, wxLEFT | wxRIGHT | wxBOTTOM, 10);

    // Scrollable browser icons(simplified)
    wxScrolledWindow *scroll = new wxScrolledWindow(
        this,
        wxID_ANY,
        wxDefaultPosition,
        wxDefaultSize,
        wxHSCROLL | wxBORDER_NONE);
    scroll->SetScrollRate(10, 0);
    scroll->SetMinSize(wxSize(-1, 110));

    wxBoxSizer *hsizer = new wxBoxSizer(wxHORIZONTAL);

    // List of browsers
    std::vector<std::pair<wxString, wxBitmap>> browsers = {
    { "Firefox",          LoadBrowserIconFirefox() },
    { "Chrome",           LoadBrowserIconGoogleChromium() },
    { "Chromium",         LoadBrowserIconChromium() },
    { "Edge (Chromium)",  LoadBrowserIconMicrosoftEdge() }
    };

    _browserButtons.clear();

    for (const auto& entry : browsers) {
        const wxString& name = entry.first;
        const wxBitmap& bmp = entry.second;

        wxBoxSizer* col = new wxBoxSizer(wxVERTICAL);

        wxBitmapToggleButton* btn =
            new wxBitmapToggleButton(scroll, wxID_ANY, bmp);

        wxStaticText* label = new wxStaticText(
            scroll, wxID_ANY, name);
        label->SetForegroundColour(wxColour(80, 80, 80));

        col->Add(btn, 0, wxALIGN_CENTER | wxBOTTOM, 4);
        col->Add(label, 0, wxALIGN_CENTER);
        hsizer->Add(col, 0, wxRIGHT, 20);

        btn->Bind(wxEVT_TOGGLEBUTTON,
                  &WizardSelectBrowserPage::OnBrowserToggleEvent,
                  this);
        _browserButtons.push_back({ name, btn });
    }

    scroll->SetSizer(hsizer);
    mainSizer->Add(scroll,
                    0,
                    wxEXPAND | wxLEFT | wxRIGHT | wxBOTTOM,
                    10);

    // Checkbox
    _chkLaunchBrowser = new wxCheckBox(
        this,
        wxID_ANY,
        "Launch browser automatically. Uncheck if browser is already running.");
    mainSizer->Add(_chkLaunchBrowser, 0, wxLEFT | wxRIGHT | wxBOTTOM, 10);

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

    wxButton *btnNext = new wxButton(this, wxID_OK, "Next");
    btnNext->Bind(wxEVT_BUTTON,
                  &WizardSelectBrowserPage::OnNextClickEvent,
                  this);
    buttonBarSizer->Add(btnNext, 0);

    mainSizer->Add(buttonBarSizer, 0, wxEXPAND | wxALL, 10);

    SetSizerAndFit(mainSizer);
    CentreOnParent();
}

void WizardSelectBrowserPage::OnBrowserToggleEvent(wxCommandEvent& event) {
    /*
        Ensure that only one browser toggle button can be active at a time.

        When a browser button is clicked, this handler deactivates all other
        buttons in ``browser_buttons`` to enforce exclusive selection.
    */
    wxWindow* clicked = dynamic_cast<wxWindow*>(event.GetEventObject());

    for (auto& pair : _browserButtons) {
        wxToggleButton* btn = pair.second;

        if (btn != clicked)
            btn->SetValue(false);
    }

    event.Skip();
}

bool WizardSelectBrowserPage::ValidateFields() {
    /*
    Validate the user's input before allowing the wizard to advance.

    This method checks that:
    * the URL field is not empty
    * a browser has been selected from the available toggle buttons

    If validation succeeds, the selected values are written to the
    wizard's shared data dictionary. If validation fails, a warning
    message is shown and the wizard remains on the current page.

    Returns
    -------
    bool
        True if the page is valid and the wizard may proceed; False if
        validation fails and navigation should be blocked.
    */
    wxString baseUrl = _txtBaseUrl->GetValue().Strip(wxString::both);
    if (baseUrl.IsEmpty()) {
        wxMessageBox("Please enter a base URL.",
            "Validation error",
            wxICON_WARNING);
        return false;
    }

    wxString selectedBrowser;
    for (const auto& pair : _browserButtons) {
        const wxString& name = pair.first;
        wxToggleButton* btn = pair.second;

        if (btn->GetValue()) {
            selectedBrowser = name;
            break;
        }
    }

    if (selectedBrowser.IsEmpty()) {
        wxMessageBox("Please select a browser.",
                     "Missing information",
                     wxICON_WARNING);
        return false;
    }

    data_->baseUrl = baseUrl;
    data_->browser = selectedBrowser;
    data_->launchBrowserAutomatically = _chkLaunchBrowser->GetValue();

    return true;
}

void WizardSelectBrowserPage::OnNextClickEvent(wxCommandEvent& event) {
    if (!ValidateFields()) {
        return;
    }

    EndModal(wxID_OK);
}

}   // namespace webweaver::studio
