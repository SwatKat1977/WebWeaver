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
// CLICK listener
// --------------------
// --------------------
// CLICK listener
// --------------------
document.addEventListener("click", function(e) {

    // INSPECT MODE → block click + send element info
    if (window.__INSPECT_MODE === true) {
        e.preventDefault();
        e.stopPropagation();

        const el = e.target;

        window.__selenium_clicked_element = {
            tag: el.tagName.toLowerCase(),
            id: el.id,
            class: el.className,
            text: el.innerText,
            css: getCssSelector(el),
            xpath: getXPath(el)
        };
    }

    // RECORD MODE → record, and for links delay navigation slightly
    if (window.__RECORD_MODE === true) {
        const el = e.target;
        const ev = {
            type: "click",
            selector: getCssSelector(el),
            xpath: getXPath(el),
            x: e.clientX,
            y: e.clientY,
            time: now()
        };

        window.__recorded_actions.push(ev);
        window.__recorded_outgoing.push(ev);

        // If the click was on (or inside) a link, delay navigation
        const link = el.closest ? el.closest("a[href]") : null;
        if (link && link.href) {
            // Stop the browser from navigating *right now*
            e.preventDefault();
            const url = link.href;

            console.log("Recorded link click, delaying navigation to:", url);

            // Give Python's 100ms poll loop time to read __recorded_outgoing
            setTimeout(() => {
                window.location.href = url;
            }, 200);
        }
    }

}, true);

// --------------------
// INPUT listener (RECORD MODE ONLY)
// --------------------
document.addEventListener("input", function(e) {
    if (!window.__RECORD_MODE) return;

    const el = e.target;
    if (!el) return;

    if (el.tagName === "INPUT" || el.tagName === "TEXTAREA") {
        const ev = {
            type: "input",
            selector: getCssSelector(el),
            xpath: getXPath(el),
            value: el.value,
            time: now()
        };
        window.__recorded_actions.push(ev);
        window.__recorded_outgoing.push(ev);
    }
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

        except Exception:
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

        except Exception:
            return

        if current_url != self._last_url:
            self._last_url = current_url
            self._handle_navigation()

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

        except Exception:
            pass

        # Re-inject JS
        self._inject_inspector_js(initial=False)

        # Restore active mode
        if self._record_active:
            self.enable_record_mode()
        elif self._inspect_active:
            self.enable_inspect_mode()
