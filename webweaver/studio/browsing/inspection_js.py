"""
This source file is part of Web Weaver
For the latest info, see https://github.com/SwatKat1977/WebWeaver

Copyright 2025-2026 Webweaver Development Team

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

INSPECTOR_JS: str = r"""
(function () {
    // Prevent double-install
    if (window.__WEBWEAVER_INSPECT_INSTALLED__) {
        return;
    }
    window.__WEBWEAVER_INSPECT_INSTALLED__ = true;

    console.log("WebWeaver Inspector installed");

    // Shared buffer for Selenium
    if (window.top) {
        window.top.__selenium_clicked_element = null;
    }

    function hoverIn(e) {
        const t = e.target;
        if (!t) return;
        t.__old_outline = t.style.outline;
        t.style.outline = "2px solid red";
    }

    function hoverOut(e) {
        const t = e.target;
        if (!t) return;
        t.style.outline = t.__old_outline || "";
        delete t.__old_outline;
    }

    function inspectClick(e) {
        const el = e.target;
        if (!el) return;

        if (window.top) {
            window.top.__selenium_clicked_element = el;
        }

        console.log("INSPECT picked element:", el);

        e.preventDefault();
        e.stopPropagation();
    }

    document.addEventListener("mouseover", hoverIn, true);
    document.addEventListener("mouseout", hoverOut, true);
    document.addEventListener("click", inspectClick, true);
    
    window.__WEBWEAVER_INSPECT_CLEANUP__ = function () {
        document.removeEventListener("mouseover", hoverIn, true);
        document.removeEventListener("mouseout", hoverOut, true);
        document.removeEventListener("click", inspectClick, true);
        delete window.__WEBWEAVER_INSPECT_INSTALLED__;
    };
})();
"""
