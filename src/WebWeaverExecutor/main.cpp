/*
This source file is part of Web Weaver
For the latest info, see https ://github.com/SwatKat1977/WebWeaver

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
*/
#include <iostream>
#include <string>
#include <CLI/CLI.hpp>
#include "SuiteParser.h"
#include "WebWeaverExceptions.h"

int main(int argc, char* argv[]) {

    CLI::App app{ "Web Weaver Test Executor" };

    std::string suite_json;
    std::string search = ".";
    std::string version = "Webweaver Test Executor 0.0.0";

    app.add_option("suite_json", suite_json, "Path to test suite JSON file")
        ->required();

    app.add_option("--search", search,
        "Path to discover listeners (default: current dir)");

    app.set_version_flag("--version", version);

    CLI11_PARSE(app, argc, argv);

    // --- USE the values directly ---
    std::cout << "Suite JSON path: " << suite_json << "\n";
    std::cout << "Search path:     " << search << "\n";
    std::cout << "Version:         " << version << "\n";

    try {
        auto parser = WebWeaver::Executor::SuiteParser("schema.json");
        auto suite = parser.LoadSuite("testsuite.json");
        std::cout << "Test suite loaded successfully." << std::endl;
        std::cout << suite.dump(4) << std::endl;
    } catch (const WebWeaver::Executor::WebWeaverException &except) {
        std::cout << "[EXCEPTION] " << except.what() << std::endl;
    } catch (const std::runtime_error& ex) {
        std::cout << "[EXCEPTION] " << ex.what() << std::endl;
    }

    return 0;
}
