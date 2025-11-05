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
import argparse
import logging
import pathlib
import sys
from suite_parser import SuiteParser
from test_executor import TestExecutor
from discoverer import discover_listeners, import_test_modules


def ensure_suite_path_on_sys_path(suite_path: str):
    suite_dir = pathlib.Path(suite_path).resolve().parent
    if str(suite_dir) not in sys.path:
        sys.path.insert(0, str(suite_dir))

def main():
    parser = argparse.ArgumentParser(description="Web Weaver Test Executor")
    parser.add_argument("suite_json", help="Path to test suite JSON file")
    parser.add_argument("--search", default=".", help="Path to discover listeners (default: current dir)")
    args = parser.parse_args()

    logger = logging.getLogger("executor")
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
    logger.addHandler(handler)

    ensure_suite_path_on_sys_path(args.suite_json)

    parser = SuiteParser("suite_schema.json")
    suite = parser.load_suite(args.suite_json)

    # Discover TestListener implementations
    listeners = discover_listeners(args.search)
    logger.info("Discovered %d TestListener(s).", len(listeners))

    executor = TestExecutor(logger)

    # Inject discovered (global) listeners into test classes safely
    for suite_test in suite.get("tests", []):
        for cls_conf in suite_test.get("classes", []):
            cls = executor._resolve_class(cls_conf["name"])

            # Ensure listener list exists
            if not hasattr(cls, "__listeners__"):
                cls.__listeners__ = []

            existing_types = {type(l) for l in cls.__listeners__}

            # Merge in only *new* listener types
            for l in listeners:  # these are from discover_listeners()
                if type(l) not in existing_types:
                    cls.__listeners__.append(l)

    results = executor.run_tests(suite)

    print("\n=== Test Results ===")
    for name, result in results.items():
        print(f"{name:40}  {result.status.name}")


if __name__ == "__main__":
    main()
