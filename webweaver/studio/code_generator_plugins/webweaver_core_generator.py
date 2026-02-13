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
import time

from webweaver.studio.code_generation.base_code_generator import \
    BaseCodeGenerator
from webweaver.studio.code_generation.base_code_generator_settings import \
    BaseCodeGeneratorSettings


class WebweaverCoreSettings(BaseCodeGeneratorSettings):
    """ Webweaver core code generator """

    def __init__(self):
        self.threaded = False
        self.use_decorators = True

    def to_json(self) -> dict:
        return {
            "threaded": self.threaded,
            "useDecorators": self.use_decorators
        }

    def from_json(self, data: dict) -> None:
        self.threaded = data.get("threaded", False)
        self.use_decorators = data.get("useDecorators", True)


class WebweaverCoreCodeGenerator(BaseCodeGenerator):
    """Webweaver core (python) code generator"""

    # pylint: disable=too-few-public-methods

    id = "webweaver-core"
    name = "Webweaver Core (Python)"
    description = "Generate Python automated script using Webweaver Core"

    def _begin_file(self):
        recording_doc = self._recording_document.data
        recording_name = recording_doc['recording']["name"]
        cls_name = recording_name.replace(' ', '')

        template = [
            "# -----------------------------------------------------------",
            "# Generated from Webweaver Studio",
            "# -----------------------------------------------------------"]
        self._lines.extend(template)

        all_events: dict = recording_doc["recording"]["events"]
        has_button_control: bool = False
        has_dropdown_control: bool = False
        has_check_control: bool = False
        has_text_control: bool = False
        has_wait: bool = False

        for event in all_events:
            if event["type"] == "dom.check":
                has_check_control = True

            elif event["type"] == "dom.click":
                has_button_control = True

            elif event["type"] == "dom.select":
                has_dropdown_control = True

            elif event["type"] == "dom.type":
                has_text_control = True

            elif event["type"] == "wait":
                has_wait = True

        if has_wait:
            self._lines.append("import time")

        self._lines.append("from webweaver.web.exceptions import ElementNotFoundError")
        self._lines.append("from webweaver.executor.test_decorators import test")

        if has_button_control:
            self._lines.append("from webweaver.web.button_control import ButtonControl")

        if has_dropdown_control:
            self._lines.append("from webweaver.web.dropdown_control import DropdownControl")

        if has_check_control:
            self._lines.append("from webweaver.web.tickbox_control import TickboxControl")

        if has_text_control:
            self._lines.append("from webweaver.web.textbox_control import TextboxControl")

        self._indent_level = 2

        class_template = [
             "",
             "",
            f"class {cls_name}(WebweaverTestClass)",
             "",
             "    @test()",
            f"    def {cls_name}(self):"]
        self._lines.extend(class_template)

    def _end_file(self):
        self._lines.append("")

    def _on_unknown(self, payload):
        return

    def on_dom_click(self, payload):
        indent = " " * (self._indent_level * 4)

        template = [
            "ctrl = ButtonControl(self._driver, self._logger)",
            "if not ctrl.find_element_by_xpath('{xpath}'):",
            "    raise ElementNotFoundError('Button not found')",
            "",
            "ctrl.click()",
            ""]
        self._lines.extend(
            indent + line.format(**payload) for line in template)

    def on_dom_type(self, payload):
        indent = " " * (self._indent_level * 4)

        template = [
            "ctrl = TextboxControl(self._driver, self._logger)",
            "if not ctrl.find_element_by_xpath('{xpath}'):",
            "    raise ElementNotFoundError('Textbox not found')",
            "",
            "ctrl.set_value('{value}')",
            ""]
        self._lines.extend(
            indent + line.format(**payload) for line in template)

    def on_dom_check(self, payload):
        indent = " " * (self._indent_level * 4)

        template = [
            "ctrl = TickboxControl(self._driver, self._logger)",
            "if not ctrl.find_element_by_xpath('{xpath}'):",
            "    raise ElementNotFoundError('TickboxControl not found')",
            "",
            "ctrl_value = {value}",
            "if ctrl_value:",
            "    ctrl.check()",
            "else:",
            "    ctrl.uncheck()",
            ""]
        self._lines.extend(
            indent + line.format(**payload) for line in template)

    def on_dom_select(self, payload):
        indent = " " * (self._indent_level * 4)

        template = [
            "ctrl = DropdownControl(self._driver, self._logger)",
            "if not ctrl.find_element_by_xpath('{xpath}'):",
            "    raise ElementNotFoundError('drop-down not found')",
            "",
            "ctrl.select_by_text('{value}')",
            ""]
        self._lines.extend(
            indent + line.format(**payload) for line in template)

    def on_nav_goto(self, payload):
        indent = " " * (self._indent_level * 4)
        nav_url: str = payload["url"]
        self._lines.append(indent + f"self._driver.open_page('{nav_url}')")

    def on_wait(self, payload):
        indent = " " * (self._indent_level * 4)
        duration_seconds: float = int(payload["duration_ms"]) / 1000

        self._lines.append(indent + f"time.sleep({duration_seconds})")
        self._lines.append("")


GENERATOR_CLASS = WebweaverCoreCodeGenerator  # pylint: disable=invalid-name
SETTINGS_CLASS = WebweaverCoreSettings        # pylint: disable=invalid-name
