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
#ifndef WEBDRIVEROPTIONPARAMETER_H_
#define WEBDRIVEROPTIONPARAMETER_H_
#include <string>
#include <unordered_map>
#include <utility>
#include <vector>
#include "BrowserType.h"
#include "WebDriverOption.h"

namespace webweaver::studio {

enum class WebDriverOptionTarget {
    ARGUMENT,
    CHROMIUM_PREF,
    FIREFOX_PREF
};

struct WebDriverOptionBinding {
    WebDriverOptionTarget target;
    std::string key;
};

class WebDriverOptionParameter {
 public:
    using BindingList = std::vector<WebDriverOptionBinding>;
    using BrowserMap  = std::unordered_map<BrowserType, BindingList>;

    WebDriverOptionParameter(
        WebDriverOption option,
        BrowserMap validFor,
        bool hasParameters = false)
        : option_(option),
          hasParameters_(hasParameters),
          validFor_(std::move(validFor))
    {}

    const BindingList* BindingsFor(BrowserType browser) const {
        auto it = validFor_.find(browser);
        return it != validFor_.end() ? &it->second : nullptr;
    }

    WebDriverOption GetOption() const {
        return option_;
    }

    bool HasParameters() const {
        return hasParameters_;
    }

    bool IsValidFor(BrowserType browser) const {
        return validFor_.find(browser) != validFor_.end();
    }

 private:
    WebDriverOption option_;
    bool hasParameters_;
    BrowserMap validFor_;
};

}   // namespace webweaver::studio

#endif  // WEBDRIVEROPTIONPARAMETER_H_
