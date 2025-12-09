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
#ifndef WIZARDSTEPINDICATOR_H_
#define WIZARDSTEPINDICATOR_H_
#include <string>
#include <vector>
#include <wx/wx.h>

namespace webweaver::studio {

class WizardStepIndicator : public wxPanel {
 public:
    WizardStepIndicator(wxWindow* parent,
                        const std::vector<std::string> steps,
                        int activeIndex = 0);

    void SetActive(int index);

 private:
    std::vector<std::string> steps_;
    std::vector<wxStaticText*> labels_;
    int activeIndex_;
};

}   // namespace webweaver::studio

#endif  // WIZARDSTEPINDICATOR_H_
