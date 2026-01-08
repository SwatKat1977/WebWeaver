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
import asyncio
import logging
import os
import pathlib
import sys
from webweaver.executor.test_suite.suite_parser import SuiteParser
from webweaver.executor.test_executor import TestExecutor
from webweaver.executor.discoverer import discover_listeners
from webweaver.version import __version__


def ensure_path_in_sys_path(logger: logging.Logger, path: str):
    """
    Ensure the directory is present on sys.path.

    This allows Python to locate and import modules within the directory.

    Args:
        logger: Logger to use
        path: The file path to be added.
    """
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))
        logger.debug(f"Added '%s' to sys.path", path)


def main():
    """
    Entry point for the Web Weaver test executor CLI.

    This function loads a test suite definition, discovers available test
    listeners, injects them into the appropriate test classes, and then
    executes all defined tests.

    Environment:
        WEBWEAVER_PATH: Must point to the root of the Web Weaver installation.
                        It is used to locate the suite schema definition.

    Command-line Arguments:
        suite_json: Path to the JSON file describing the test suite to run.
        --search: Optional directory to search for TestListener implementations
                  (default: current working directory).

    Workflow:
        1. Validates the WEBWEAVER_PATH environment variable.
        2. Configures logging for the test executor.
        3. Ensures the test suite directory is added to sys.path.
        4. Loads the test suite via SuiteParser using the suite schema.
        5. Discovers TestListener implementations dynamically.
        6. Injects discovered listeners into each test class.
        7. Executes all tests through TestExecutor.
        8. Prints a summary of test results to stdout.

    Exits gracefully if the WEBWEAVER_PATH environment variable is missing.
    """
    # pylint: disable=too-many-locals
    webweaver_root = os.getenv("WEBWEAVER_PATH", None)

    if not webweaver_root:
        print("Please set WEBWEAVER_PATH environment variable.")
        return

    parser = argparse.ArgumentParser(description="Web Weaver Test Executor")
    parser.add_argument("suite_json",
                        help="Path to test suite JSON file")
    parser.add_argument("--search", default=".",
                        help="Path to discover listeners (default: current dir)")
    parser.add_argument("--version", action="version",
                        version=f"Webweaver Test Executor {__version__}")
    args = parser.parse_args()

    logger = logging.getLogger("executor")
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
    logger.addHandler(handler)

    logger.info("Web Weaver Test Executor %s", __version__)
    logger.info("Copyright 2025 Webweaver development team")
    logger.info("Distributed under the GNU General Public License V2")

    suite_dir = str(pathlib.Path(args.suite_json).resolve().parent)
    ensure_path_in_sys_path(logger, suite_dir)
    ensure_path_in_sys_path(logger, args.search)

    if not os.path.isfile(args.suite_json):
        logger.critical("Test suite JSON file '%s' not found", args.suite_json)
        return

    suite_schema_file: str = os.path.join(webweaver_root, "suite_schema.json")
    if not os.path.isfile(suite_schema_file):
        logger.critical("Test suite schema file '%s' not found",
                        suite_schema_file)
        return

    parser = SuiteParser(suite_schema_file)
    suite = parser.load_suite(args.suite_json)

    # Discover TestListener implementations
    listeners = discover_listeners(logger, args.search)
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

            # Merge in only *new* listener types from discover_listeners()
            for listener in listeners:
                if type(listener) not in existing_types:
                    cls.__listeners__.append(listener)

    results = asyncio.run(executor.run_tests(suite))

    print("\n=== Test Results ===")
    for name, result in results.items():
        print(f"{name:40}  {result.status.name}")


if __name__ == "__main__":
    main()
