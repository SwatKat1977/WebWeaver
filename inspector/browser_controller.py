"""
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
"""
import os
import time
import json
from selenium.webdriver.support.ui import WebDriverWait
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, WebDriverException


class BrowserController:
    """
    Controls a Chrome browser instance with custom JavaScript injection for
    DOM-element inspection and event recording.

    The controller manages two primary modes:
    - **Inspect Mode**: Clicking elements returns detailed DOM metadata.
    - **Record Mode**: Captures outgoing UI interaction events.

    The controller listens for navigation changes, automatically reinjects
    the inspector script on new pages, and ensures the active mode persists
    across page loads.

    Parameters
    ----------
    callback : callable
        A function accepting a JSON string. Used to receive click/record events
        detected inside the browser.
    """

    def __init__(self, callback):
        """
        Initializes the BrowserController.

        Sets up Chrome with custom options, loads the inspector JavaScript file,
        and launches a WebDriver session.

        Parameters
        ----------
        callback : callable
            Function invoked with JSON-encoded event payloads originating from
            the page (click inspector results or recorded events).
        """
        self.callback = callback
        self.inspect_active = False
        self.record_active = False

        # Find inspector script
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.js_path = os.path.join(base_dir, "js", "inspector.js")

        # Chrome launch options
        options = Options()
        options.add_argument("--disable-web-security")
        options.add_argument("--disable-site-isolation-trials")
        options.add_argument("--disable-features=IsolateOrigins,site-per-process")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", True)

        self.driver = webdriver.Chrome(options=options)

    def inject_inspector_js(self, initial=False):
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
        print("Loading inspector.js from:", self.js_path)

        with open(self.js_path, "r", encoding="utf8") as f:
            inspector_js = f.read()

        print("Injecting inspector.js...")

        # Always register CDP script so it loads on EVERY navigation
        self.driver.execute_cdp_cmd(
            "Page.addScriptToEvaluateOnNewDocument",
            {"source": inspector_js}
        )

        # Inject into CURRENT document ONLY during the initial load
        if initial:
            self.driver.execute_script(inspector_js)

        print("Inspector injected.")

    def open_page(self, url):
        """
        Navigates the browser to a given URL and injects the inspector script.

        Parameters
        ----------
        url : str
            The webpage URL to load.
        """
        self.driver.get(url)
        # inject immediately on first load
        self.inject_inspector_js(initial=True)

    # ---------------------
    # Modes
    # ---------------------
    def enable_inspect_mode(self):
        """
        Enables DOM inspection mode.

        When active:
        - Clicking an element stores metadata in
          `window.__selenium_clicked_element`.
        - Record mode is disabled.
        """
        self.inspect_active = True
        self.record_active = False

        self.driver.execute_script("window.__INSPECT_MODE = true;")
        self.driver.execute_script("window.__RECORD_MODE = false;")
        self.driver.execute_script("window.__FORCE_INSPECT_MODE = true;")

    def disable_inspect_mode(self):
        """
        Disables DOM inspection mode.

        Clears inspector-related state flags in the page.
        """
        self.inspect_active = False
        self.driver.execute_script("window.__INSPECT_MODE = false;")
        self.driver.execute_script("window.__FORCE_INSPECT_MODE = false;")

    def enable_record_mode(self):
        """
        Enables event recording mode.

        When active:
        - UI interaction events are collected into `window.__recorded_outgoing`.
        - Inspect mode is disabled.
        """
        self.record_active = True
        self.inspect_active = False

        self.driver.execute_script("window.__RECORD_MODE = true;")
        self.driver.execute_script("window.__INSPECT_MODE = false;")
        self.driver.execute_script("window.__FORCE_INSPECT_MODE = false;")

    def disable_record_mode(self):
        """
        Disables event recording mode.

        Stops pushing events into the recording buffer.
        """
        self.record_active = False
        self.driver.execute_script("window.__RECORD_MODE = false;")

    def listen_for_click(self):
        """
        Starts a continuous loop that monitors page navigation, element clicks,
        and recorded events.

        Behaviour:
        ----------
        - Detects page navigation and reinjects inspector.js automatically.
        - Restores active mode (inspect or record) after navigation.
        - Retrieves clicked-element data stored by inspector mode.
        - Retrieves batches of recorded user-interaction events.
        - Deduplicates recorded events before sending them to the callback.

        This loop runs indefinitely until an exception is encountered
        (typically when the WebDriver is closed).
        """
        last_url = None

        while True:
            try:
                current_url = self.driver.current_url

                # Navigation detection
                if current_url != last_url:
                    print(f"[INFO] Navigation detected: {last_url} -> {current_url}")
                    last_url = current_url

                    # Wait for new page to load
                    try:
                        WebDriverWait(self.driver, 10).until(
                            lambda d: d.execute_script("return document.readyState") == "complete"
                        )
                    except TimeoutException:
                        pass

                    print("[INFO] Reinjecting inspector into new page...")
                    # Use initial=False to prevent double-injection
                    self.inject_inspector_js(initial=False)

                    # Restore whichever mode was active
                    if self.inspect_active:
                        print("[INFO] Inspect Active → enabling inspect mode")
                        self.enable_inspect_mode()
                        self.disable_record_mode()

                    elif self.record_active:
                        print("[INFO] Record Active → enabling record mode")
                        self.enable_record_mode()

                    else:
                        print("[INFO] No mode active → disabling both modes")
                        self.disable_inspect_mode()
                        self.disable_record_mode()

                # Inspector element selection
                result = self.driver.execute_script(
                    "return window.__selenium_clicked_element || null;"
                )

                if result:
                    self.driver.execute_script(
                        "window.__selenium_clicked_element = null;")
                    self.callback(json.dumps(result, indent=2))

                # Recorder events
                events = self.driver.execute_script(
                    "return window.__recorded_outgoing || [];")

                if events:
                    self.driver.execute_script("window.__recorded_outgoing = [];")

                    deduped = []
                    seen = set()

                    for ev in events:
                        # create a signature that identifies identical events
                        sig = (
                            ev.get("type"),
                            ev.get("selector"),
                            ev.get("xpath"),
                            ev.get("x"),
                            ev.get("y")
                        )

                        if sig not in seen:
                            seen.add(sig)
                            deduped.append(ev)

                    # send deduped events to callback
                    for ev in deduped:
                        self.callback(json.dumps(ev, indent=2))

                time.sleep(0.1)

            except WebDriverException:
                break
