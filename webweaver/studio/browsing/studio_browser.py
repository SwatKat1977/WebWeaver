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
import logging
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.ui import WebDriverWait


BROWSER_JS_INJECTION: str = r"""
console.log("Inspector script injected.");

// --------------------
// Typing debounce state
// --------------------
const __typing_timers = new Map();
const __typing_last_value = new Map();

// Global buffered state
window.__INSPECT_MODE = window.__INSPECT_MODE || false;
window.__FORCE_INSPECT_MODE = window.__FORCE_INSPECT_MODE || false;
window.__RECORD_MODE = window.__RECORD_MODE || false;

window.__recorded_actions = window.__recorded_actions || [];
window.__recorded_outgoing = window.__recorded_outgoing || [];

function now() { return Date.now(); }

// Restore Inspect Mode after navigation only if requested
if (window.__FORCE_INSPECT_MODE === true) {
    window.__INSPECT_MODE = true;
}

// Disable inspect mode if not used
if (window.__FORCE_INSPECT_MODE === false) {
    window.__INSPECT_MODE = false;
}

function __record_type_if_text_input(el) {
    if (!el) return;

    if (el.tagName === "TEXTAREA") {
        // ok
    } else if (el.tagName === "INPUT") {
        const t = (el.type || "").toLowerCase();
        if (!["text","email","password","search","url","number"].includes(t)) {
            return;
        }
    } else {
        return;
    }

    const value = (typeof el.value === "string") ? el.value : "";
    if (!value) return;

    const ev = {
        __kind: "type",
        selector: getCssSelector(el),
        xpath: getXPath(el),
        value: value,
        time: now()
    };

    window.__recorded_actions.push(ev);
    window.__recorded_outgoing.push(ev);
}

function __is_text_input(el) {
    if (!el) return false;

    if (el.tagName === "TEXTAREA") return true;

    if (el.tagName === "INPUT") {
        const t = (el.type || "").toLowerCase();
        return ["text", "email", "password", "search", "url", "number"].includes(t);
    }

    return false;
}

function __flush_typing(el) {
    // Only ever flush REAL text inputs
    if (!__is_text_input(el)) return;

    // Always trust the live DOM value
    const value = (typeof el.value === "string") ? el.value : "";
    if (value === "") return; // don't record empty garbage

    const ev = {
        __kind: "type",
        selector: getCssSelector(el),
        xpath: getXPath(el),
        value: value,
        time: now()
    };

    // ---- coalesce ----
    const arr = window.__recorded_actions;
    const last = arr.length > 0 ? arr[arr.length - 1] : null;

    if (
        last &&
        last.__kind === "type" &&
        last.selector === ev.selector
    ) {
        // Replace last
        last.value = ev.value;
        last.time = ev.time;

        const out = window.__recorded_outgoing;
        if (out.length > 0) {
            const lastOut = out[out.length - 1];
            if (
                lastOut.__kind === "type" &&
                lastOut.selector === ev.selector
            ) {
                lastOut.value = ev.value;
                lastOut.time = ev.time;
            } else {
                out.push(ev);
            }
        }
    } else {
        window.__recorded_actions.push(ev);
        window.__recorded_outgoing.push(ev);
    }

    __typing_last_value.delete(el);

    if (__typing_timers.has(el)) {
        clearTimeout(__typing_timers.get(el));
        __typing_timers.delete(el);
    }
}

function getCssSelector(el) {
    if (el.id) return "#" + el.id;
    if (el.className)
        return el.tagName.toLowerCase() + "." +
               el.className.trim().replace(/\s+/g, ".");
    return el.tagName.toLowerCase();
}

window.__drain_recorded_events = function() {
    const out = window.__recorded_outgoing || [];
    window.__recorded_outgoing = [];
    return out;
}

function getXPath(el) {
    if (el.id) return `//*[@id="${el.id}"]`;
    const parts = [];
    while (el && el.nodeType === 1) {
        let index = 1;
        let sibling = el.previousSibling;
        while (sibling) {
            if (sibling.nodeType === 1 && sibling.nodeName === el.nodeName) index++;
            sibling = sibling.previousSibling;
        }
        parts.unshift(el.nodeName + "[" + index + "]");
        el = el.parentNode;
    }
    return "/" + parts.join("/");
}

// --------------------
// Hover highlight (INSPECT MODE ONLY)
// --------------------
function hoverListener(e) {
    if (!window.__INSPECT_MODE && !window.__RECORD_MODE) return;
    e.target.__old_outline = e.target.style.outline;
    e.target.style.outline = "2px solid red";
}

function outListener(e) {
    if (!window.__INSPECT_MODE && !window.__RECORD_MODE) return;
    e.target.style.outline = e.target.__old_outline || "";
    delete e.target.__old_outline;
}

// --------------------
// INPUT listener (RECORD MODE ONLY, DEBOUNCED)
// --------------------
document.addEventListener("input", function(e) {
    if (!window.__RECORD_MODE) return;

    const el = e.target;
    if (!el) return;

    if (el.tagName === "TEXTAREA") {
        // ok
    } else if (el.tagName === "INPUT") {
        const t = (el.type || "").toLowerCase();
        if (t !== "text" && t !== "email" && t !== "password" && t !== "search" && t !== "url" && t !== "number") {
            return; // not a text field
        }
    } else {
        return;
    }

    // Remember latest value
    __typing_last_value.set(el, el.value);

    // Clear existing timer
    if (__typing_timers.has(el)) {
        clearTimeout(__typing_timers.get(el));
    }

    // Start / restart debounce timer
    const timer = setTimeout(() => {
        __flush_typing(el);
    }, 400);

    __typing_timers.set(el, timer);

}, true);

// --------------------
// CHANGE listener (text inputs, checkbox, radio, select)
// --------------------
document.addEventListener("change", function(e) {
    if (!window.__RECORD_MODE) return;

    const el = e.target;
    if (!el) return;

    // TEXT INPUTS
    __record_type_if_text_input(el);

    // CHECKBOX / RADIO
    if (el.tagName === "INPUT") {
        const t = (el.type || "").toLowerCase();
        if (t === "checkbox" || t === "radio") {

            const ev = {
                __kind: "check",
                selector: getCssSelector(el),
                xpath: getXPath(el),
                checked: el.checked,
                time: now()
            };

            window.__recorded_actions.push(ev);
            window.__recorded_outgoing.push(ev);
            return;
        }
    }

    // SELECT
    if (el.tagName === "SELECT") {
        const ev = {
            __kind: "select",
            selector: getCssSelector(el),
            xpath: getXPath(el),
            value: el.value,
            time: now()
        };

        window.__recorded_actions.push(ev);
        window.__recorded_outgoing.push(ev);
        return;
    }

}, true);

document.addEventListener("submit", function(e) {
    if (!window.__RECORD_MODE) return;

    const form = e.target;
    if (!form) return;

    const inputs = form.querySelectorAll("input, textarea");
    for (const el of inputs) {
        __record_type_if_text_input(el);
    }
}, true);

// --------------------
// BLUR listener (force flush typing immediately)
// --------------------
document.addEventListener("blur", function(e) {
    if (!window.__RECORD_MODE) return;
    __record_type_if_text_input(e.target);
}, true);

// --------------------
// MOUSEDOWN listener: flush pending typing before clicks
// --------------------
document.addEventListener("mousedown", function() {
    if (!window.__RECORD_MODE) return;

    for (const el of __typing_last_value.keys()) {
        if (!__is_text_input(el)) continue;

        __flush_typing(el);
        setTimeout(() => __flush_typing(el), 250);
    }
}, true);

// --------------------
// CLICK listener
// --------------------
document.addEventListener("click", function(e) {
    if (!window.__RECORD_MODE) return;

    const el = e.target;
    if (!el) return;

    const ev = {
        __kind: "click",
        selector: getCssSelector(el),
        xpath: getXPath(el),
        x: e.clientX,
        y: e.clientY,
        time: now()
    };

    window.__recorded_actions.push(ev);
    window.__recorded_outgoing.push(ev);
}, true);

// --------------------
// Hover listeners
// --------------------
document.addEventListener("mouseover", hoverListener, true);
document.addEventListener("mouseout", outListener, true);
"""


class StudioBrowser:
    """
    High-level wrapper around a Selenium WebDriver instance used by WebWeaver Studio.

    This class acts as the single integration point between the Studio application and
    the underlying browser automation engine (Selenium).

    Responsibilities:
    - Provide a stable, high-level API for browser interaction
    - Centralise navigation, lifecycle management, and utilities (screenshots, etc)
    - Act as an abstraction layer so the rest of the application does not depend directly
      on Selenium APIs
    - Serve as a future extension point for recording actions, logging, retries, waits,
      and error handling

    The raw Selenium driver is intentionally hidden behind this wrapper. If low-level
    access is required, it can be obtained via the `raw` property.
    """

    def __init__(self, driver, logger: logging.Logger):
        """
        Create a new StudioBrowser wrapper.

        :param driver: An already-initialised Selenium WebDriver instance.
        """
        self._driver = driver
        self._logger = logger.getChild(__name__)

        self._inspect_active = False
        self._record_active = False
        self._last_url = None

    @property
    def inspect_active(self):
        """
        Check whether DOM inspection mode is currently active.

        When inspection mode is enabled, user clicks in the browser will be
        intercepted and metadata about the clicked element will be written
        into the page context for retrieval by the Studio application.

        :return: True if inspection mode is active, False otherwise.
        """
        return self._inspect_active

    @property
    def record_active(self):
        """
        Check whether event recording mode is currently active.

        When recording mode is enabled, user interaction events (clicks, inputs,
        navigation, etc) are captured inside the page and buffered for later
        retrieval via `pop_recorded_events()`.

        :return: True if recording mode is active, False otherwise.
        """
        return self._record_active

    def open_page(self, url: str):
        """
        Navigate the browser to the specified URL.

        :param url: Absolute or relative URL to navigate to.
        """
        self._driver.get(url)

        self._last_url = url
        # inject immediately on first load
        self._inject_inspector_js(initial=True)

    def quit(self):
        """
        Close the browser and shut down the underlying WebDriver instance.
        """
        self._driver.quit()

    def screenshot(self, path: str):
        """
        Save a screenshot of the current browser viewport.

        :param path: File path where the screenshot will be written.
        """
        self._driver.save_screenshot(path)

    def execute_script(self, script):
        """
        Execute arbitrary JavaScript in the context of the currently loaded page.

        This is a thin passthrough to Selenium's `execute_script` API and should
        be used sparingly. Prefer adding higher-level methods to StudioBrowser
        instead of scattering raw JavaScript calls throughout the codebase.

        :param script: JavaScript source code to execute.
        :return: The value returned by the executed script, if any.
        """
        return self._driver.execute_script(script)

    @property
    def raw(self):
        """
        Get the underlying Selenium WebDriver instance.

        This should be used sparingly and only when access to Selenium-specific APIs
        is required that are not yet wrapped by StudioBrowser.

        :return: The raw Selenium WebDriver instance.
        """
        return self._driver

    def is_alive(self) -> bool:
        """
        Check whether the underlying browser session is still alive.

        This method performs a trivial operation against the WebDriver to determine
        whether the browser process and session are still valid. If the browser has
        been closed, crashed, or the session has become invalid, Selenium will raise
        an exception which is caught and interpreted as the browser being not alive.

        :return: True if the browser session is still active and responsive,
                 False if the browser is no longer available.
        """
        try:
            # Any trivial call that touches the browser
            _ = self._driver.title
            return True

        except WebDriverException:
            return False

    def enable_inspect_mode(self):
        """
        Enables DOM inspection mode.

        When active:
        - Clicking an element stores metadata in
          `window.__selenium_clicked_element`.
        - Record mode is disabled.
        """
        self._inspect_active = True
        self._record_active = False

        self._driver.execute_script("window.__INSPECT_MODE = true;")
        self._driver.execute_script("window.__RECORD_MODE = false;")
        self._driver.execute_script("window.__FORCE_INSPECT_MODE = true;")

    def disable_inspect_mode(self):
        """
        Disables DOM inspection mode.

        Clears inspector-related state flags in the page.
        """
        self._inspect_active = False
        self._driver.execute_script("window.__INSPECT_MODE = false;")
        self._driver.execute_script("window.__FORCE_INSPECT_MODE = false;")

    def enable_record_mode(self):
        """
        Enables event recording mode.

        When active:
        - UI interaction events are collected into `window.__recorded_outgoing`.
        - Inspect mode is disabled.
        """
        self._record_active = True
        self._inspect_active = False

        self._driver.execute_script("window.__RECORD_MODE = true;")
        self._driver.execute_script("window.__INSPECT_MODE = false;")
        self._driver.execute_script("window.__FORCE_INSPECT_MODE = false;")

    def disable_record_mode(self):
        """
        Disables event recording mode.

        Stops pushing events into the recording buffer.
        """
        self._record_active = False
        self._driver.execute_script("window.__RECORD_MODE = false;")

    def pop_recorded_events(self) -> list[dict]:
        """
        Retrieve and clear any recorded user interaction events from the page.

        This calls into the injected recording script and drains its internal
        event buffer. If recording is not active, or if the page does not yet
        have the recording infrastructure injected, this returns an empty list.

        This method is designed to be safe to call repeatedly and will never
        raise if the browser or page is in a transient state.

        :return: A list of event dictionaries describing recorded user actions.
        """

        try:
            return self._driver.execute_script(
                ("return window.__drain_recorded_events ? "
                 "window.__drain_recorded_events() : [];"))

        except WebDriverException:
            return []

    def poll(self) -> None:
        """
        Poll the browser for navigation changes and reinject scripts if needed.

        This method is intended to be called periodically by the Studio application
        (e.g. from a timer or main loop). It checks whether the browser has navigated
        to a different URL since the last poll, and if so:

        - Waits for the new document to finish loading
        - Re-injects the inspector/recorder JavaScript
        - Restores the previously active mode (inspect or record)

        If the browser is no longer reachable or is in an invalid state, this
        method fails silently.
        """
        try:
            current_url = self._driver.current_url

        except WebDriverException:
            return

        if current_url != self._last_url:
            self._last_url = current_url
            self._handle_navigation()

    def poll_inspected_element(self):
        """
        Poll the browser for a newly inspected (clicked) DOM element.

        This method checks for the presence of a temporary JavaScript-side variable
        (`window.__selenium_clicked_element`) which is set by the injected inspector
        script when the user clicks an element in the page.

        If an element is found, the variable is immediately cleared in the page so
        the same element is not returned again on the next poll.

        Returns:
            The Selenium WebElement if a new element was picked, otherwise None.

        This method is safe to call repeatedly (e.g. from a timer or idle handler).
        If the browser is not available, the page has navigated, or script execution
        fails, None is returned.
        """

        try:
            el = self._driver.execute_script(
                "return window.__selenium_clicked_element || null;")
            if el:
                self._driver.execute_script("window.__selenium_clicked_element = null;")

            return el

        except WebDriverException:
            return None

    def _inject_inspector_js(self, initial=False):
        """
        Injects the inspector.js script into the browser context.

        The script is:
        - Registered with Chrome DevTools Protocol so that it automatically runs
          on every new document load.
        - Optionally executed immediately in the currently loaded page.

        Parameters
        ----------
        initial : bool
            If True, the script is executed immediately in the current DOM.
            If False, only CDP registration is performed.
        """

        self._logger.info("Injecting web browser javascript: Started")

        # Always register CDP script so it loads on EVERY navigation
        self._driver.execute_cdp_cmd(
            "Page.addScriptToEvaluateOnNewDocument",
            {"source": BROWSER_JS_INJECTION})

        # Inject into CURRENT document ONLY during the initial load
        if initial:
            self._driver.execute_script(BROWSER_JS_INJECTION)

        self._logger.info("Injecting web browser javascript: Completed")

    def _handle_navigation(self) -> None:
        """
        Handle post-navigation setup after the browser changes page.

        This method:

        - Waits (briefly) for the DOM to reach the 'complete' ready state
        - Re-injects the inspector/recorder JavaScript into the new page
        - Restores whichever mode (inspect or record) was active before navigation

        This is called automatically by `poll()` when a URL change is detected.
        """

        # Wait for DOM ready
        try:
            WebDriverWait(self._driver, 10).until(
                lambda d: d.execute_script(
                    "return document.readyState") == "complete")

        except WebDriverException:
            pass

        # Re-inject JS
        self._inject_inspector_js(initial=False)

        # Restore active mode
        if self._record_active:
            self.enable_record_mode()
        elif self._inspect_active:
            self.enable_inspect_mode()
