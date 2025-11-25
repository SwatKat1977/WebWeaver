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
#include <vector>
#include "pybind11/embed.h"
#include "pybind11/stl.h"
#include "CLI/CLI.hpp"
#include "SuiteParser.h"
#include "WebWeaverExceptions.h"

// py::scoped_interpreter guard{};

std::vector<pybind11::object> discover_listeners(const std::string& search_path) {
    std::vector<pybind11::object> found_listeners;

    std::filesystem::path root = std::filesystem::absolute(search_path);

    std::cout << "[DEBUG] Scanning for listeners in: " << root << "\n";

    // Import necessary Python modules
    pybind11::object importlib = pybind11::module_::import("importlib.util");
    pybind11::object inspect = pybind11::module_::import("inspect");

    // Import TestListener base class
    pybind11::object testlistener_mod = pybind11::module_::import("yourmodule.TestListener");
    pybind11::object TestListener = testlistener_mod.attr("TestListener");

    // Walk files
    for (auto& entry : std::filesystem::recursive_directory_iterator(root))
    {
        if (!entry.is_regular_file())
            continue;

        auto path = entry.path();
        if (path.filename().string().rfind("listener_", 0) != 0) continue;
        if (path.extension() != ".py") continue;

        std::cout << "[DEBUG] Importing: " << path << "\n";

        try {
            // module name (no .py)
            std::string mod_name = path.stem().string();

            // spec = importlib.util.spec_from_file_location(...)
            pybind11::object spec = importlib.attr("spec_from_file_location")(
                mod_name,
                path.string()
                );

            // module = importlib.util.module_from_spec(spec)
            pybind11::object module = importlib.attr("module_from_spec")(spec);

            // spec.loader.exec_module(module)
            spec.attr("loader").attr("exec_module")(module);

            // Loop members in module
            for (auto item : module.attr("__dict__"))
            {
                auto value = item.second;

                if (pybind11::isinstance(value, pybind11::type::of(TestListener)))
                {
                    // Exclude base TestListener itself
                    if (value.is(TestListener))
                        continue;

                    std::cout << "[FOUND] Listener: "
                        << std::string(pybind11::str(value.attr("__name__"))) << "\n";

                    // Instantiate class -> listener instance
                    found_listeners.push_back(value());
                }
            }
        }
        catch (std::exception& e)
        {
            std::cout << "[WARN] Could not import " << path << ": " << e.what() << "\n";
        }
    }

    // Deduplicate by class name
    std::map<std::string, pybind11::object> unique;
    for (auto& l : found_listeners) {
        unique[(std::string)pybind11::str(l.get_type().attr("__name__"))] = l;
    }

    std::cout << "[DEBUG] Discovered: \n";
    for (auto& p : unique) {
        std::cout << "  -> " << p.first << "\n";
    }

    std::vector<pybind11::object> result;
    for (auto& p : unique)
        result.push_back(p.second);

    return result;
}

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
