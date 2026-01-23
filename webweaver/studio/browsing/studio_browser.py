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
from selenium.common.exceptions import (WebDriverException,
                                        TimeoutException,
                                        ElementClickInterceptedException,
                                        StaleElementReferenceException)
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from browsing.inspection_js import INSPECTOR_JS
from browsing.recording_js import RECORDING_JS, RECORDING_ENABLE_BOOTSTRAP


@dataclass
class PlaybackStepResult:
    ok: bool
    error: str = ""

    @staticmethod
    def ok():
        return PlaybackStepResult(True, "")

    @staticmethod
    def fail(msg: str):
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
        try:
            # Any trivial call that touches the browser
            _ = self._driver.title
            return True

        except WebDriverException:
            return False

    # --------------------------------------------------------------
    # Inspection functionality
    # --------------------------------------------------------------

    def enable_inspect_mode(self):
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
        if not self._cdp_record_installed:
            self._driver.execute_cdp_cmd(
                "Page.addScriptToEvaluateOnNewDocument",
                {"source": RECORDING_JS}
            )
            self._cdp_record_installed = True

        # Ensure installed in the current document too
        self._driver.execute_script(RECORDING_JS)

    def enable_record_mode(self):
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

        print("ENABLE CHECK:",
              self._driver.execute_script(
                  "return [window.__WW_REC_INSTALLED__, window.__WW_RECORD_ENABLED__];"
              ))

    def disable_record_mode(self):
        """
        Disables event recording mode.
        """
        self._record_active = False

        # Disable in current page
        try:
            self._driver.execute_script("window.__WW_RECORD_ENABLED__ = false;")

        except Exception:
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
        try:
            return self._driver.execute_script(
                "return window.__drain_recorded_events ? "
                "window.__drain_recorded_events() : [];")

        except Exception as e:
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
                "return arguments[0].id ? '#' + arguments[0].id : arguments[0].tagName.toLowerCase();",
                el
            )

            xpath = self._driver.execute_script(
                """
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
                el
            )

            return {
                "tag": tag,
                "id": el_id,
                "class": cls,
                "text": text,
                "css": css,
                "xpath": xpath,
            }

        except Exception:
            return {
                "tag": None,
                "id": None,
                "class": None,
                "text": None,
                "css": None,
                "xpath": None,
            }

    def playback_click(self, payload: dict) -> PlaybackStepResult:
        xpath = payload.get("xpath")

        try:
            element = self.wait_for_xpath(xpath, timeout=10)

            self.scroll_into_view(element)
            self.highlight(element)

            try:
                element.click()
            except ElementClickInterceptedException:
                # Try once more after scroll/highlight
                self.scroll_into_view(element)
                element.click()

            self.wait_for_page_settle()

            return PlaybackStepResult.ok()

        except TimeoutException:
            return PlaybackStepResult.fail(
                f"Timeout waiting for element: {xpath}")

        except StaleElementReferenceException:
            return PlaybackStepResult.fail(f"Element became stale: {xpath}")

        except Exception as ex:
            return PlaybackStepResult.fail(str(ex))

    def playback_type(self, payload: dict) -> PlaybackStepResult:
        xpath = payload.get("xpath")
        text = payload.get("text", "")

        try:
            element = self.wait_for_xpath(xpath, timeout=10)

            self.scroll_into_view(element)
            self.highlight(element)

            element.clear()
            element.click()
            element.send_keys(text)

            return PlaybackStepResult.ok()

        except TimeoutException:
            return PlaybackStepResult.fail(f"Timeout waiting for element: {xpath}")

        except StaleElementReferenceException:
            return PlaybackStepResult.fail(f"Element became stale: {xpath}")

        except Exception as ex:
            return PlaybackStepResult.fail(str(ex))

    def wait_for_ready_state(self, timeout: float = 10.0):
        """
        Wait until document.readyState == 'complete'.
        """
        WebDriverWait(self._driver, timeout).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )

    def wait_for_dom_stable(self, timeout: float = 10.0, stable_time: float = 0.5):
        """
        Wait until the DOM size stops changing for `stable_time` seconds.
        """
        import time

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

        raise TimeoutError("DOM did not stabilize in time")

    def wait_for_page_settle(self, timeout: float = 10.0):
        """
        Wait for page load + DOM to stabilize.
        """
        self.wait_for_ready_state(timeout)
        self.wait_for_dom_stable(timeout)

    def wait_for_xpath(self, xpath: str, timeout: float = 10.0):
        """
        Wait until an element exists and is visible.
        """
        return WebDriverWait(self._driver, timeout).until(
            EC.visibility_of_element_located((By.XPATH, xpath))
        )

    def scroll_into_view(self, element):
        """
        Scroll element into the center of the viewport.
        """
        self._driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center', inline: 'center'});",
            element,
        )

    def highlight(self, element, duration: float = 0.25):
        """
        Visually highlight an element during playback.
        """
        import time

        try:
            original = element.get_attribute("style")
            self._driver.execute_script(
                "arguments[0].setAttribute('style', arguments[1]);",
                element,
                "outline: 3px solid red; outline-offset: 2px;",
            )
            time.sleep(duration)
            self._driver.execute_script(
                "arguments[0].setAttribute('style', arguments[1]);",
                element,
                original,
            )

        except Exception:
            pass  # highlighting must never break playback
