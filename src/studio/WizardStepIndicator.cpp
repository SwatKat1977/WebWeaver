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
#include <string>
#include <vector>
#include "WizardStepIndicator.h"

namespace webweaver::studio {

WizardStepIndicator::WizardStepIndicator(wxWindow* parent,
                                         const std::vector<std::string> steps,
                                         int activeIndex)
    : wxPanel(parent), steps_(steps) {

    wxBoxSizer* sizer = new wxBoxSizer(wxHORIZONTAL);

    for (size_t i = 0; i < steps.size(); ++i) {
        wxStaticText* label = new wxStaticText(this, wxID_ANY, "");
        sizer->Add(label, 0, wxRIGHT | wxALIGN_CENTER_VERTICAL, 20);
        labels_.push_back(label);
    }

    SetSizer(sizer);
    SetActive(activeIndex_);
}

void WizardStepIndicator::SetActive(int index) {
    if (index < 0 || index >= static_cast<int>(steps_.size())) {
        return;
    }

    activeIndex_ = index;

    for (size_t i = 0; i < labels_.size(); ++i) {
        wxString bullet = (i == static_cast<int>(index))
            ? wxT("\u25CF") : wxT("\u25CB");

        labels_[i]->SetLabel(bullet + " " + steps_[i]);

        if (i == static_cast<int>(index)) {
            // Active = black
            labels_[i]->SetForegroundColour(wxColour(0, 0, 0));
        } else {
            // Inactive = grey
            labels_[i]->SetForegroundColour(wxColour(130, 130, 130));
        }
    }

    Layout();
    Refresh();
}

}   // namespace webweaver::studio
