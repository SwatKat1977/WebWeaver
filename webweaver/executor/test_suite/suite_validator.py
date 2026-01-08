"""
This source file is part of Web Weaver
For the latest info, see https://github.com/SwatKat1977/WebWeaver

Copyright 2025-2026 Webweaver Development Team

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
from jsonschema import validate, ValidationError


class TestSuiteValidationFailed(Exception):
    """ Test suite JSON schema validation failure exception """


def validate_suite(data: dict, schema: dict) -> None:
    """
    Validate suite data against JSON schema.
    Raises TestSuiteValidationFailed on error.
    """
    try:
        validate(instance=data, schema=schema)
    except ValidationError as ex:
        raise TestSuiteValidationFailed(ex.message) from ex
