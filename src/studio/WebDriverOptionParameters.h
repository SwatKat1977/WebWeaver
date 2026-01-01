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
#ifndef WEBDRIVEROPTIONPARAMETERS_H_
#define WEBDRIVEROPTIONPARAMETERS_H_
#include <unordered_map>
#include "WebDriverOptionParameter.h"

namespace webweaver::studio {

inline const std::unordered_map<WebDriverOption, WebDriverOptionParameter>
WebDriverOptionParameters = {

    { WebDriverOption::DISABLE_EXTENSIONS,
      { WebDriverOption::DISABLE_EXTENSIONS,
        {
            { BrowserType::CHROME, {
                { WebDriverOptionTarget::ARGUMENT, "--disable-extensions" }
            }},
            { BrowserType::EDGE, {
                { WebDriverOptionTarget::ARGUMENT, "--disable-extensions" }
            }}
        }
      }
    },

    { WebDriverOption::DISABLE_NOTIFICATIONS,
      {
        WebDriverOption::DISABLE_NOTIFICATIONS,
        {
            { BrowserType::CHROME, {
                { WebDriverOptionTarget::CHROMIUM_PREF,
                  "profile.default_content_setting_values.notifications" }
            }},
            { BrowserType::EDGE, {
                { WebDriverOptionTarget::CHROMIUM_PREF,
                  "profile.default_content_setting_values.notifications" }
            }},
            { BrowserType::CHROMIUM, {
                { WebDriverOptionTarget::CHROMIUM_PREF,
                  "profile.default_content_setting_values.notifications" }
            }},
            { BrowserType::FIREFOX, {
                { WebDriverOptionTarget::FIREFOX_PREF,
                  "permissions.default.desktop-notification" }
            }}
        }
      }
    },

    { WebDriverOption::MAXIMISED,
      { WebDriverOption::MAXIMISED,
        {
            { BrowserType::CHROME, {
                { WebDriverOptionTarget::ARGUMENT, "--start-maximized" }
            }},
            { BrowserType::EDGE, {
                { WebDriverOptionTarget::ARGUMENT, "--start-maximized" }
            }}
        }
      }
    },

    { WebDriverOption::PRIVATE,
      { WebDriverOption::PRIVATE,
        {
            { BrowserType::CHROME, {
                { WebDriverOptionTarget::ARGUMENT, "--incognito" }
            }},
            { BrowserType::EDGE, {
                { WebDriverOptionTarget::ARGUMENT, "--inprivate" }
            }}
        }
      }
    },

    { WebDriverOption::WINDOW_SIZE,
      { WebDriverOption::WINDOW_SIZE,
        {
            { BrowserType::CHROME, {
                { WebDriverOptionTarget::ARGUMENT, "--window-size" }
            }},
            { BrowserType::EDGE, {
                { WebDriverOptionTarget::ARGUMENT, "--window-size" }
            }}
        },
        true
      }
    },

    { WebDriverOption::USER_AGENT,
      { WebDriverOption::USER_AGENT,
        {
            { BrowserType::CHROME, {
                { WebDriverOptionTarget::ARGUMENT, "--user-agent" }
            }},
            { BrowserType::EDGE, {
                { WebDriverOptionTarget::ARGUMENT, "--user-agent" }
            }},
            { BrowserType::FIREFOX, {
                { WebDriverOptionTarget::FIREFOX_PREF,
                  "general.useragent.override" }
            }}
        },
        true
      }
    }
};

}   // namespace webweaver::studio

#endif  // WEBDRIVEROPTIONPARAMETERS_H_
