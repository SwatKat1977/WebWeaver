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
#ifndef SOLUTIONCREATEWIZARD_WIZARDBEHAVIOURPAGE_H_
#define SOLUTIONCREATEWIZARD_WIZARDBEHAVIOURPAGE_H_
#include <wx/wx.h>
#include <wx/collpane.h>
#include "SolutionCreateWizard/SolutionCreateWizardBasePage.h"
#include "StudioDefinitions.h"

namespace webweaver::studio {

class WizardBehaviourPage : public wxDialog {
 public:
    WizardBehaviourPage(wxWindow* parent,
                        ProjectCreateWizardData* data,
                        StepsList steps);

 private:
    // wxWidgets event handlers require non-const wxCommandEvent&
    // NOLINTNEXTLINE(runtime/references)
    void OnNextClickEvent(wxCommandEvent& event);

    // Recording behaviour controls
    wxCheckBox* chkPrivate_ = nullptr;
    wxCheckBox* chkDisableExtensions_ = nullptr;
    wxCheckBox* chkDisableNotifications_ = nullptr;
    wxCheckBox* chkIgnoreCertErrors_ = nullptr;

    wxRadioButton* radioDefaultWindowSize_ = nullptr;
    wxRadioButton* radioMaximised_ = nullptr;
    wxRadioButton* radioCustomWindowSize_ = nullptr;
    wxTextCtrl* txtWindowWidth_ = nullptr;
    wxTextCtrl* txtWindowHeight_ = nullptr;

    wxCollapsiblePane* advancedPane_ = nullptr;
    wxTextCtrl* txtUserAgent_ = nullptr;

    ProjectCreateWizardData *data_;
    StepsList steps_;


    void CreateBehaviourPanel(wxBoxSizer* parent);
    void SyncWindowSizeState();
};

}   // namespace webweaver::studio

#endif  // SOLUTIONCREATEWIZARD_WIZARDBEHAVIOURPAGE_H_
