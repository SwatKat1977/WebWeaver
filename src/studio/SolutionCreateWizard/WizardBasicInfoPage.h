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
#ifndef PROJECTCREATEWIZARD_WIZARDBASICINFOPAGE_H_
#define PROJECTCREATEWIZARD_WIZARDBASICINFOPAGE_H_
#include <wx/wx.h>
#include <string>
#include <vector>
#include "WizardStepIndicator.h"
#include "SolutionCreateWizard/SolutionCreateWizardBasePage.h"

namespace webweaver::studio {

class WizardBasicInfoPage : public wxDialog {
 public:
    WizardBasicInfoPage(wxWindow* parent,
                        ProjectCreateWizardData *data,
                        std::vector<std::string> steps);

 private:
    ProjectCreateWizardData* data_;
    std::vector<std::string> steps_;

    wxTextCtrl *txtSolutionName_;
    wxTextCtrl *txtSolutionDir_;
    wxCheckBox* chkCreateSolutionDir_;

    bool ValidateFields();

    // wxWidgets event handlers require non-const wxCommandEvent&
    // NOLINTNEXTLINE(runtime/references)
    void OnBrowseSolutionLocation(wxCommandEvent& event);

    // wxWidgets event handlers require non-const wxCommandEvent&
    // NOLINTNEXTLINE(runtime/references)
    void OnNextClickEvent(wxCommandEvent& event);
};

}   // namespace webweaver::studio

#endif  // PROJECTCREATEWIZARD_WIZARDBASICINFOPAGE_H_
