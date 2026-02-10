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
from webweaver.studio.code_generation.base_code_generator import \
    BaseCodeGenerator
from webweaver.studio.code_generation.base_code_generator_settings import \
    BaseCodeGeneratorSettings


class WebweaverCoreSettings(BaseCodeGeneratorSettings):
    """ Example code generator """

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


class ExampleDebugGenerator(BaseCodeGenerator):
    """Temporary code generator as an example"""
    # pylint: disable=too-few-public-methods

    id = "example-debug"
    name = "Example Debug Generator"
    description = "Outputs a dummy file for testing the plugin system"

    def _begin_file(self):
        recording_name = self._recording_document.data['recording']["name"]
        cls_name = recording_name.replace(' ', '')

        template = [
            "# Example Debug Generator generated code",
            "# Copyright 2025-2026 Webweaver Development Team",
            "",
            f"class {cls_name}(WebweaverTestClass)",
             "",
             "    @test()",
            f"    def {cls_name}(self):"
        ]
        self._lines.extend(template)

        self._indent_level = 2
        print(f"\n\nClass Name: {cls_name}")

    def _end_file(self):
        return

    def _on_unknown(self, payload):
        return

    def on_dom_click(self, payload):
        return

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
        return

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
        return

    def on_wait(self, payload):
        return


GENERATOR_CLASS = ExampleDebugGenerator # pylint: disable=invalid-name
SETTINGS_CLASS = WebweaverCoreSettings  # pylint: disable=invalid-name
