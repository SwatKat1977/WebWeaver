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

class BrowserController:

    def __init__(self, callback):
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

    # ---------------------
    # JS injection
    # ---------------------
    def inject_inspector_js(self):
        print("Loading inspector.js from:", self.js_path)

        with open(self.js_path, "r", encoding="utf8") as f:
            inspector_js = f.read()

        print("Injecting inspector.js...")

        # Ensure script is injected in REAL page context (critical)
        self.driver.execute_cdp_cmd(
            "Page.addScriptToEvaluateOnNewDocument",
            {"source": inspector_js}
        )

        # Also execute immediately on the current page
        self.driver.execute_script(inspector_js)

        print("Inspector injected.")

    def open_page(self, url):
        self.driver.get(url)
        self.inject_inspector_js()

    # ---------------------
    # Modes
    # ---------------------
    def enable_inspect_mode(self):
        self.inspect_active = True
        self.record_active = False

        self.driver.execute_script("window.__INSPECT_MODE = true;")
        self.driver.execute_script("window.__RECORD_MODE = false;")
        self.driver.execute_script("window.__FORCE_INSPECT_MODE = true;")

    def disable_inspect_mode(self):
        self.inspect_active = False
        self.driver.execute_script("window.__INSPECT_MODE = false;")
        self.driver.execute_script("window.__FORCE_INSPECT_MODE = false;")

    def enable_record_mode(self):
        self.record_active = True
        self.inspect_active = False

        self.driver.execute_script("window.__RECORD_MODE = true;")
        self.driver.execute_script("window.__INSPECT_MODE = false;")
        self.driver.execute_script("window.__FORCE_INSPECT_MODE = false;")

    def disable_record_mode(self):
        self.record_active = False
        self.driver.execute_script("window.__RECORD_MODE = false;")

    # ---------------------
    # Event listener loop
    # ---------------------
    def listen_for_click(self):
        last_url = None

        while True:
            try:
                current_url = self.driver.current_url

                # Navigation detection
                if current_url != last_url:
                    print(f"[INFO] Navigation detected: {last_url} -> {current_url}")
                    last_url = current_url

                    try:
                        WebDriverWait(self.driver, 10).until(
                            lambda d: d.execute_script("return document.readyState") == "complete"
                        )
                    except:
                        pass

                    print("[INFO] Reinjecting inspector into new page...")
                    self.inject_inspector_js()

                    # Restore mode on navigation
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
                    self.driver.execute_script("window.__selenium_clicked_element = null;")
                    self.callback(json.dumps(result, indent=2))

                # Recorder events
                events = self.driver.execute_script("return window.__recorded_outgoing || [];")

                if events:
                    self.driver.execute_script("window.__recorded_outgoing = [];")
                    for ev in events:
                        self.callback(json.dumps(ev, indent=2))

                time.sleep(0.1)

            except Exception:
                break
