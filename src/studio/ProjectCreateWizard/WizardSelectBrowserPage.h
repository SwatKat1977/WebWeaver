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
#ifndef WIZARDSELECTBROWSERPAGE_H_
#define WIZARDSELECTBROWSERPAGE_H_
#include <string>
#include <wx/wx.h>

/*
from project_create_wizard.browser_icons import (
    CHROMIUM_BROWSER_ICON,
    CHROME_BROWSER_ICON,
    FIREFOX_BROWSER_ICON,
    MICROSOFT_EDGE_BROWSER_ICON)
from bitmap_utils import BitmapUtils
from wizard_step_indicator import WizardStepIndicator
from project_create_wizard.wizard_ids import ID_BACK_BUTTON
*/

class WizardWebSelectBrowserPage : public wxDialog {
    const std::string DEFAULT_URL = "https://www.example.com";

    WizardWebSelectBrowserPage(wxWindow* parent, int data);

    void OnBrowserToggleEvent(wxCommandEvent& event);

    bool ValidateFields();

    void OnNextEvent(wxCommandEvent& event);
};

#endif  // WIZARDSELECTBROWSERPAGE_H_
