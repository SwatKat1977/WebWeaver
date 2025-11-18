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
import json
from jsonschema import validate, ValidationError
from webweaver.web.web_driver_option import WebDriverOption
from webweaver.web.browser_type import BrowserType
from webweaver.web.web_weaver_config import WebWeaverConfig

DEFAULT_SCHEMA_FILE: str = "webweaver_config.schema.json"


def load_webweaver_config(path: str,
                          schema_path: str = DEFAULT_SCHEMA_FILE) \
        -> WebWeaverConfig:
    """
    Load WebWeaverConfig from JSON, validate against schema,
    and convert string values into enums.
    """
    # Load JSON config
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Load JSON Schema
    with open(schema_path, "r", encoding="utf-8") as f:
        schema = json.load(f)

    # Validate the JSON structure
    try:
        validate(instance=data, schema=schema)
    except ValidationError as e:
        raise ValueError(f"Config validation failed: {e.message}")

    # ---- Convert browser_type ----
    data["browser_type"] = BrowserType[data["browser_type"].upper()]

    # ---- Convert browser_options ----
    raw_options = data.get("browser_options", None)
    converted_options = None

    if raw_options is not None:
        converted_options = []

        for opt in raw_options:
            opt_name = opt[0].upper()
            option_enum = WebDriverOption[opt_name]

            if len(opt) == 1:
                converted_options.append((option_enum,))
            else:
                converted_options.append((option_enum, str(opt[1])))

        data["browser_options"] = converted_options

    # Construct validated dataclass
    return WebWeaverConfig(**data)


config = load_webweaver_config(
    "example_configurations/webweaver_config.json",
    "example_configurations/webweaver_config.schema.json")
print(config)
