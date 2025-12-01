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
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


class BrowserController:
    """Controls a Chrome WebDriver instance and injects the custom
    ``inspector.js`` script into loaded pages.

    This class manages browser automation for the Inspector tool:
    - Launches Chrome with custom options
    - Loads pages
    - Injects the Inspector JavaScript
    - Communicates selection events back to wxPython via callback
    """

    def __init__(self, callback):
        """Initialize the BrowserController.

        Parameters
        ----------
        callback : callable
            Function that receives JSON data whenever the user selects
            an element inside the browser window. Typically a wxPython handler.
        """
        self.callback = callback

        # Find inspector.js based on this file's directory
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.js_path = os.path.join(base_dir, "js", "inspector.js")

        # Chrome Options
        options = Options()
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-extensions")
        options.add_argument("--log-level=3")
        options.add_experimental_option("excludeSwitches",
                                        ["enable-logging"])

        self.driver = webdriver.Chrome(options=options)

    def open_page(self, url):
        """Open the given URL and inject the inspector script.

        Parameters
        ----------
        url : str
            The webpage URL to navigate to.
        """
        self.driver.get(url)
        self.inject_inspector_js()

    def inject_inspector_js(self):
        """Load and inject the inspector.js script into the active webpage."""
        print("Loading inspector.js from:", self.js_path)

        with open(self.js_path, "r", encoding="utf8") as f:
            inspector_js = f.read()

        print("Injecting inspector.js...")
        self.driver.execute_script(inspector_js)
        print("Inspector injected.")

    def force_reinject_inspector(self):
        """
        Re-inject the inspector script, printing errors if something fails.
        """

        try:
            print("[INFO] Forcing inspector reinjection...")
            self.inject_inspector_js()
            print("[INFO] Inspector reinjected successfully.")
        except Exception as e:
            print("[ERROR] Reinjection failed:", e)

    def enable_inspect_mode(self):
        """Enable element inspect mode inside the webpage."""
        self.driver.execute_script("window.__INSPECT_MODE = true;")

    def disable_inspect_mode(self):
        """Disable element inspect mode inside the webpage."""
        self.driver.execute_script("window.__INSPECT_MODE = false;")

    def listen_for_click(self):
        """Checks every 100ms if JS stored an element selection."""
        while True:
            try:
                result = self.driver.execute_script(
                    "return window.__selenium_clicked_element || null;"
                )
                if result:
                    # Clear it to allow new selections
                    self.driver.execute_script(
                        "window.__selenium_clicked_element = null;"
                    )
                    # Send to wxPython callback
                    self.callback(json.dumps(result, indent=2))
                time.sleep(0.1)
            except Exception:
                # Example: browser closed
                break
