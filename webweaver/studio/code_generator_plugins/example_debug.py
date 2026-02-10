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

    def generate(self, recording_document, settings) -> str:
        return f"""\
# This is a test generator
{recording_document}
# Recording path: {recording_document.path}
 
def test_dummy():
    assert True
"""


GENERATOR_CLASS = ExampleDebugGenerator
SETTINGS_CLASS = WebweaverCoreSettings
