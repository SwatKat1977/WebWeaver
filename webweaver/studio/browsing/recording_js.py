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

RECORDING_JS = r"""
(function () {
    if (window.__WW_REC_INSTALLED__) return;
    window.__WW_REC_INSTALLED__ = true;

    if (typeof window.__WW_RECORD_ENABLED__ === "undefined") {
        window.__WW_RECORD_ENABLED__ = false;
    }

    window.__recorded_outgoing = [];

    window.__drain_recorded_events = function () {
        var out = window.__recorded_outgoing;
        window.__recorded_outgoing = [];
        return out;
    };

    function now() { return Date.now(); }

    function getXPath(el) {
        if (el.id) return '//*[@id="' + el.id + '"]';

        var parts = [];
        while (el && el.nodeType === 1) {
            var index = 1;
            var sibling = el.previousSibling;
            while (sibling) {
                if (sibling.nodeType === 1 && sibling.nodeName === el.nodeName) {
                    index++;
                }
                sibling = sibling.previousSibling;
            }
            parts.unshift(el.nodeName.toLowerCase() + "[" + index + "]");
            el = el.parentNode;
        }
        return "/" + parts.join("/");
    }

    document.addEventListener("mousedown", function (e) {
        if (!window.__WW_RECORD_ENABLED__) return;

        var el = e.target;

        var ev = {
            __kind: "click",
            xpath: getXPath(el),
            time: now()
        };

        window.__recorded_outgoing.push(ev);
    }, true);

    console.log("WW RECORDER INSTALLED");
})();
"""

RECORDING_ENABLE_BOOTSTRAP = r"""
window.__WW_RECORD_ENABLED__ = true;
"""
