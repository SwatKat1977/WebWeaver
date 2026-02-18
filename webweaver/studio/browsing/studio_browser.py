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
from dataclasses import dataclass
import logging
import time
from selenium.common.exceptions import (WebDriverException,
                                        TimeoutException,
                                        ElementClickInterceptedException,
                                        StaleElementReferenceException,
                                        JavascriptException)
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from webweaver.studio.browsing.inspection_js import INSPECTOR_JS
from webweaver.studio.browsing.recording_js import RECORDING_JS


class PlaybackActionError(RuntimeError):
    """Raised when a playback action fails semantically."""


@dataclass
class PlaybackStepResult:
    """
    Result object representing the outcome of executing a single playback step.

    This class is used as the uniform return type for all playback operations
    (e.g. click, type, select, check, navigate). It encapsulates whether the
    operation succeeded and, if not, a human-readable error message describing
    the failure.

    PlaybackStepResult is intentionally simple and serialisable so it can be
    easily passed between the playback engine and the UI layer.

    :ivar ok: True if the playback step completed successfully, False otherwise.
    :ivar error: Human-readable error message describing the failure. Empty if ok is True.
    """
    ok: bool
    error: str = ""

    @staticmethod
    def success():
        """
        Create a PlaybackStepResult representing a successful playback step.

        :return: A PlaybackStepResult with ok=True and an empty error message.
        """
        return PlaybackStepResult(True, "")

    @staticmethod
    def fail(msg: str):
        """
        Create a PlaybackStepResult representing a failed playback step.

        :param msg: Human-readable error message describing the failure.
        :return: A PlaybackStepResult with ok=False and the given error message.
        """
        return PlaybackStepResult(False, msg)


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
    # pylint: disable=too-many-instance-attributes, too-many-public-methods

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
        self._cdp_inspect_installed = False
        self._cdp_record_installed = False
        self._cdp_record_enable_script_id = None

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
        # pylint: disable=broad-exception-caught
        if not self._driver:
            return False

        try:
            # Any trivial call that touches the browser
            _ = self._driver.title
            return True

        except Exception:
            return False

    # --------------------------------------------------------------
    # Page scroll functionality
    # --------------------------------------------------------------

    def scroll_to_bottom(self):
        """
        Scroll the browser window to the bottom of the current page.
        """
        self._driver.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);")

    def scroll_to_top(self):
        """
        Scroll the browser window to the top of the current page.
        """
        self._driver.execute_script("window.scrollTo(0, 0);")

    def scroll_to(self, x, y):
        """
        Scroll the browser window to a specific position.

        Parameters
        ----------
        x : int
            The horizontal scroll offset.
        y : int
            The vertical scroll offset.
        """
        self._driver.execute_script(f"window.scrollTo({x}, {y});")

    # --------------------------------------------------------------
    # Inspection functionality
    # --------------------------------------------------------------

    def enable_inspect_mode(self):
        """
        Enable DOM inspection mode in the browser.

        This switches the browser into inspection-only mode by enabling the injected
        inspector script and disabling recording. While inspection mode is active,
        user interactions are visually highlighted and described but are not recorded
        into the active Recording.

        This operation only affects the currently loaded document; future navigations
        will rely on the standard injection bootstrap mechanisms.
        """
        self._inspect_active = True
        self._record_active = False
        self._driver.execute_script(INSPECTOR_JS)

    def disable_inspect_mode(self):
        """
        Disables DOM inspection mode.
        """
        self._inspect_active = False
        self._driver.execute_script(
            "window.__WEBWEAVER_INSPECT_CLEANUP__ && "
            "window.__WEBWEAVER_INSPECT_CLEANUP__();")

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
                "return window.top.__selenium_clicked_element || null;"
            )

            if el:
                self._driver.execute_script(
                    "window.top.__selenium_clicked_element = null;"
                )

            return el

        except WebDriverException:
            return None

    def _inject_inspector_js(self) -> None:
        self._logger.info("Injecting 'inspect' javascript: Started")

        if not self._cdp_inspect_installed:
            self._driver.execute_cdp_cmd(
                "Page.addScriptToEvaluateOnNewDocument",
                {"source": INSPECTOR_JS})
            self._cdp_inspect_installed = True

        # Inject into current page
        self._driver.execute_script(INSPECTOR_JS)

        self._logger.info("Injecting 'inspect' javascript: Completed")

    # --------------------------------------------------------------
    # Recording functionality
    # --------------------------------------------------------------

    def _ensure_recording_js_installed(self) -> None:
        """
        Ensure that the recording JavaScript is installed in the browser.

        This method installs the core recording script in two places:
          1. As a CDP bootstrap script so it is automatically injected into all
             future documents.
          2. Directly into the currently loaded document.

        This guarantees that the recording infrastructure is available both for the
        current page and for any subsequent navigations or cross-domain transitions.

        The installation is idempotent: the CDP bootstrap is only registered once.
        """
        if not self._cdp_record_installed:
            self._driver.execute_cdp_cmd(
                "Page.addScriptToEvaluateOnNewDocument",
                {"source": RECORDING_JS}
            )
            self._cdp_record_installed = True

        # Ensure installed in the current document too
        self._driver.execute_script(RECORDING_JS)

    def enable_record_mode(self):
        """
        Enable event recording mode in the browser.

        This ensures that the recording infrastructure is installed in both the
        current document and all future documents, and sets the global recording
        enable flag so user interactions are captured and buffered by the injected
        recorder.

        Recording mode is enabled in two stages:
          1. The core recording JavaScript is installed (if not already present).
          2. A CDP bootstrap flag is registered so future documents start with
             recording enabled, and the flag is also set in the current document.

        This method is safe to call multiple times.
        """
        self._record_active = True

        # Ensure recorder exists everywhere
        self._ensure_recording_js_installed()

        # Install ENABLE flag bootstrap for all FUTURE documents
        if not self._cdp_record_enable_script_id:
            result = self._driver.execute_cdp_cmd(
                "Page.addScriptToEvaluateOnNewDocument",
                {"source": "window.__WW_RECORD_ENABLED__ = true;"}
            )
            # Chrome returns an identifier sometimes, sometimes not; store anyway
            self._cdp_record_enable_script_id = result.get("identifier")

        # Enable in CURRENT document
        self._driver.execute_script("window.__WW_RECORD_ENABLED__ = true;")

    def disable_record_mode(self):
        """
        Disables event recording mode.
        """
        self._record_active = False

        # Disable in current page
        try:
            self._driver.execute_script("window.__WW_RECORD_ENABLED__ = false;")

        except (WebDriverException, JavascriptException):
            pass

        # Remove the bootstrap so future documents default to false again
        if self._cdp_record_enable_script_id:
            try:
                self._driver.execute_cdp_cmd(
                    "Page.removeScriptToEvaluateOnNewDocument",
                    {"identifier": self._cdp_record_enable_script_id})
            except WebDriverException:
                pass

            self._cdp_record_enable_script_id = None

    def pop_recorded_events(self) -> list[dict]:
        """
        Retrieve and clear any recorded browser events from the injected recorder.

        This method calls into the injected JavaScript bridge
        (window.__drain_recorded_events) to atomically fetch and clear the buffered
        list of recorded DOM events accumulated since the last call.

        If the recorder is not present (e.g. the page has not yet been injected, a
        navigation is in progress, or the browser session has ended), this method
        fails gracefully and returns an empty list.

        This method never raises an exception: failures to communicate with the
        browser or execute the injected JavaScript are treated as "no events
        available" and result in an empty list being returned.

        :return: A list of recorded event dictionaries (possibly empty).
        """
        try:
            return self._driver.execute_script(
                "return window.__drain_recorded_events ? "
                "window.__drain_recorded_events() : [];")

        except (WebDriverException, JavascriptException) as e:
            print("POP ERROR:", e)
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
            self._on_navigation()

    def _on_navigation(self) -> None:
        try:
            WebDriverWait(self._driver, 10).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
        except WebDriverException:
            pass

        if self._record_active:
            # Re-enable recording flag in the new document
            self._driver.execute_script("window.__WW_RECORD_ENABLED__ = true;")

    # --------------------------------------------------------------
    # Playback functionality
    # --------------------------------------------------------------

    def describe_element(self, el):
        """
        Convert a Selenium WebElement into a serialisable description dictionary.

        :param el: Selenium WebElement
        :return: dict with tag, id, class, text, css, xpath
        """
        try:
            tag = el.tag_name
            el_id = el.get_attribute("id")
            cls = el.get_attribute("class")
            text = el.text

            css = self._driver.execute_script(
                "return arguments[0].id ? '#' + arguments[0].id : "
                "arguments[0].tagName.toLowerCase();", el)

            xpath = self._driver.execute_script(
                r"""
                function getXPath(el) {
                    if (el.id) return '//*\[@id="' + el.id + '"]';
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
                return getXPath(arguments[0]);
                """,
                el)

            return {
                "tag": tag,
                "id": el_id,
                "class": cls,
                "text": text,
                "css": css,
                "xpath": xpath,
            }

        except (StaleElementReferenceException, WebDriverException,
                JavascriptException):
            return {
                "tag": None,
                "id": None,
                "class": None,
                "text": None,
                "css": None,
                "xpath": None,
            }

    def playback_click(self, payload: dict) -> PlaybackStepResult:
        """
        Replay a recorded DOM click action.

        This method locates the target element using the recorded XPath, scrolls it
        into view, optionally _highlights it for visual feedback, and performs a
        click. If the click is initially intercepted by another element, a single
        retry is performed after re-scrolling.

        After the click, the browser is allowed to settle (page load and DOM
        stabilisation) before returning.

        The operation is fully synchronous and deterministic: this method will not
        return until either the click has completed and the page has stabilised, or
        a failure has occurred.

        :param payload: Event payload containing at least:
                        - "xpath": XPath of the element to click.
        :return: A PlaybackStepResult indicating success or describing the failure.
        """
        xpath = payload.get("xpath")

        def do_click(element):
            try:
                element.click()
                return

            except ElementClickInterceptedException:
                self._logger.debug(
                    "Click intercepted — falling back to JS click")

            except WebDriverException as ex:
                self._logger.debug("Native click failed: %s", ex)

            # semantic fallback (important)
            self._driver.execute_script("arguments[0].click();", element)

        return self._playback_element(xpath, do_click, settle_after=True)

    def playback_type(self, payload: dict) -> PlaybackStepResult:
        """
        Replay a recorded text input action.

        This method locates the target input element using the recorded XPath,
        scrolls it into view, _highlights it for visual feedback, clears any existing
        content, focuses the element, and sends the recorded text via synthetic
        key events.

        The operation waits for the element to become available before interacting
        with it and fails cleanly if the element cannot be found or becomes invalid
        due to DOM changes.

        :param payload: Event payload containing:
                        - "xpath": XPath of the input element.
                        - "text": Text to type into the element.
        :return: A PlaybackStepResult indicating success or describing the failure.
        """
        xpath = payload.get("xpath")
        text = payload.get("value", "")

        def do_type(element):
            # Clear using JS (more reliable)
            self._driver.execute_script("""
                const el = arguments[0];
                el.focus();
                el.value = "";
                el.dispatchEvent(new Event('input', { bubbles: true }));
                el.dispatchEvent(new Event('change', { bubbles: true }));
            """, element)

            element.clear()
            element.click()
            element.send_keys(text)

        return self._playback_element(xpath, do_type, wait_after=False)

    def playback_check(self, payload: dict) -> PlaybackStepResult:
        """
        Replay a recorded checkbox or radio-button state change.

        This method locates the target input element using the recorded XPath and
        ensures that its checked state matches the recorded value. The element is
        not blindly toggled: if it is already in the desired state, no action is
        performed.

        If a click is required to change the state and the click is intercepted, a
        single retry is performed after re-scrolling.

        After interaction, the final state is verified to ensure the control
        reflects the requested value.

        :param payload: Event payload containing:
                        - "xpath": XPath of the checkbox/radio element.
                        - "value": Desired state (truthy for checked, falsy for unchecked).
        :return: A PlaybackStepResult indicating success or describing the failure.
        """
        xpath = payload.get("xpath")
        desired_value = payload.get("value")

        def do_check(element):
            should_be_checked = bool(desired_value)
            is_checked = element.is_selected()

            if should_be_checked != is_checked:
                element.click()

            if element.is_selected() != should_be_checked:
                raise PlaybackActionError(
                    "Checkbox/radio state did not change as expected")

        return self._playback_element(xpath, do_check)

    def playback_select(self, payload: dict) -> PlaybackStepResult:
        """
        Replay a recorded <select> (dropdown) value change.

        This method locates the target <select> element using the recorded XPath,
        scrolls it into view, _highlights it for visual feedback, and selects the
        requested option using Selenium's Select helper.

        Selection is performed either by option value or by visible text, depending
        on which field is present in the payload. After selection, the chosen option
        is verified and the page is allowed to settle in case the change triggers
        navigation or dynamic updates.

        This method only supports native HTML <select> elements. Custom, script-
        driven dropdowns should be recorded and replayed as click sequences.

        :param payload: Event payload containing:
                        - "xpath": XPath of the <select> element.
                        - "value": (Optional) Option value to select.
                        - "text": (Optional) Visible text of the option to select.
        :return: A PlaybackStepResult indicating success or describing the failure.
        """
        xpath = payload.get("xpath")
        value = payload.get("value")
        text = payload.get("text")

        def do_select(element):
            select = Select(element)

            if value is not None:
                select.select_by_value(str(value))
            elif text is not None:
                select.select_by_visible_text(str(text))
            else:
                raise PlaybackActionError("No value/text provided for select")

            # Verify result
            selected = select.first_selected_option
            if value is not None:
                if selected.get_attribute("value") != str(value):
                    raise PlaybackActionError(
                        f"Select did not change to value {value}")
            else:
                if selected.text.strip() != str(text).strip():
                    raise PlaybackActionError(
                        f"Select did not change to text '{text}'")

        return self._playback_element(xpath, do_select, settle_after=True)

    def _is_in_fixed_overlay(self, element) -> bool:
        """
        Return True if the element is inside a position:fixed container.
        Page scrolling will not move it.
        """
        return self._driver.execute_script("""
            let el = arguments[0];

            while (el) {
                const style = window.getComputedStyle(el);

                if (style.position === "fixed") {
                    return true;
                }

                el = el.parentElement;
            }

            return false;
        """, element)

    def _prepare_element_for_action(self, element):
        """
        Prepare an element for interaction.

        This intentionally does only minimal, safe work:
        - scroll element into view (centered)
        - no layout changes
        - no action-specific logic
        """

        try:
            # Skip scrolling if element is inside fixed overlay
            if self._is_in_fixed_overlay(element):
                return

            self._driver.execute_script("""
                arguments[0].scrollIntoView({
                    block: 'center',
                    inline: 'nearest'
                });
            """, element)

        except Exception:
            # Preparation should never fail playback
            pass

    def _playback_element(self,
                          xpath: str,
                          action,
                          *,
                          settle_after: bool = False,
                          wait_after: bool = True,
                          timeout: float = 10.0,
                          retries: int = 2) -> PlaybackStepResult:
        # pylint: disable=too-many-arguments

        for attempt in range(retries):
            try:
                element = self._wait_for_xpath(xpath, timeout=timeout)

                self._prepare_element_for_action(element)
                self._highlight(element)

                action(element)

                if wait_after:
                    if settle_after:
                        self._wait_for_page_settle(timeout)
                    else:
                        self._wait_for_dom_stable(timeout=1.0, stable_time=0.3)

                return PlaybackStepResult.success()

            except TimeoutException:
                return PlaybackStepResult.fail(
                    f"Timeout waiting for element: {xpath}")

            except StaleElementReferenceException:
                if attempt < retries - 1:
                    # DOM churn: try again
                    continue
                return PlaybackStepResult.fail(f"Element became stale: {xpath}")

            except (WebDriverException,
                    JavascriptException,
                    PlaybackActionError) as ex:

                if attempt < retries - 1:
                    continue

                return PlaybackStepResult.fail(str(ex))

    def _wait_for_ready_state(self, timeout: float = 10.0):
        """
        Wait until document.readyState == 'complete'.
        """
        WebDriverWait(self._driver, timeout).until(
            lambda d: d.execute_script("return document.readyState") == "complete")

    def _wait_for_dom_stable(self,
                             timeout: float = 10.0,
                             stable_time: float = 0.5):
        """
        Wait until the document is fully loaded and the DOM size stops changing
        for `stable_time` seconds.

        This is used as a heuristic to detect that the UI has reached an idle
        state after navigation or dynamic updates (e.g. in SPAs).
        """
        # First ensure the document is fully loaded
        self._wait_for_ready_state(timeout)

        end_time = time.time() + timeout
        last_count = None
        stable_since = None

        while time.time() < end_time:
            count = self._driver.execute_script(
                "return document.getElementsByTagName('*').length"
            )

            if count == last_count:
                if stable_since is None:
                    stable_since = time.time()
                elif time.time() - stable_since >= stable_time:
                    return
            else:
                stable_since = None

            last_count = count
            time.sleep(0.1)

        raise TimeoutException("DOM did not stabilize in time")

    def _wait_for_page_settle(self, timeout: float = 10.0):
        """
        Wait for page load + DOM to stabilize.
        """
        self._wait_for_ready_state(timeout)
        self._wait_for_dom_stable(timeout)

    def _wait_for_xpath(self, xpath: str, timeout: float = 10.0):
        """
        Wait until an element exists and is visible.
        """
        return WebDriverWait(self._driver, timeout).until(
            EC.presence_of_element_located((By.XPATH, xpath)))

    def _highlight(self, element, duration: float = 0.25):
        """
        Visually _highlight an element during playback.
        """
        try:
            original = element.get_attribute("style")
            self._driver.execute_script(
                "arguments[0].setAttribute('style', arguments[1]);",
                element,
                "outline: 3px solid red; outline-offset: 2px;")
            time.sleep(duration)
            self._driver.execute_script(
                "arguments[0].setAttribute('style', arguments[1]);",
                element,
                original)

        except (StaleElementReferenceException, WebDriverException, JavascriptException):
            pass  # _highlighting must never break playback
