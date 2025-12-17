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
#ifndef PROJECTCREATEWIZARD_WIZARDSELECTBROWSERPAGE_H_
#define PROJECTCREATEWIZARD_WIZARDSELECTBROWSERPAGE_H_
#include <wx/wx.h>
#include <wx/tglbtn.h>
#include <string>
#include <vector>
#include "ProjectCreateWizard/ProjectCreateWizardBasePage.h"

namespace webweaver::studio {

class WizardSelectBrowserPage : public wxDialog {
 public:
    const std::string DEFAULT_URL = "https://www.example.com";

    WizardSelectBrowserPage(wxWindow* parent,
                            ProjectCreateWizardData* data,
                            std::vector<std::string> steps);

 private:
    ProjectCreateWizardData* data_;
    std::vector<std::string> steps_;
    std::vector<std::pair<wxString, wxToggleButton*>> _browserButtons;

    wxTextCtrl *_txtBaseUrl;
    wxCheckBox *_chkLaunchBrowser;

    bool ValidateFields();

    void OnBrowserToggleEvent(wxCommandEvent& event);
    void OnNextClickEvent(wxCommandEvent& event);
};

}   // namespace webweaver::studio

#endif  // PROJECTCREATEWIZARD_WIZARDSELECTBROWSERPAGE_H_
