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
#include <filesystem>
#include <fstream>
#include <jsoncons/json.hpp>
#include <jsoncons_ext/jsonschema/jsonschema.hpp>
#include "SuiteParser.h"
#include "WebWeaverExceptions.h"

namespace WebWeaver { namespace Executor {

SuiteParser::SuiteParser(const std::string& schemaFile) {
    //using namespace std;

    // Try to open the file
    std::ifstream file(schemaFile);
    if (!file.is_open()) {
        throw TestSuiteSchemaFileNotFound(
            "Suite schema file '" + schemaFile + "' not found."
        );
    }

    try {
        // Parse JSON from file
        file >> suiteSchema_;
    }
    catch (const nlohmann::json::parse_error& ex) {
        // ex.what() contains parse detail, but we replicate Python structure
        std::string msg =
            "Invalid JSON in schema file " + schemaFile + ": " + ex.what();
        throw TestSuiteSchemaParseFailed(msg);
    }
}

nlohmann::json SuiteParser::LoadSuite(const std::string& filePath) {
    // --------------------------------------------------------------
    // Check that the test suite exists
    // --------------------------------------------------------------
    if (!std::filesystem::exists(filePath)) {
        throw TestSuiteFileNotFound(
            "Suite file '" + filePath + "' not found."
        );
    }

    // --------------------------------------------------------------
    // Load file based on extension
    // --------------------------------------------------------------
    nlohmann::json data;

    try {
        if (filePath.ends_with(".json")) {
            std::ifstream f(filePath);
            if (!f.is_open()) {
                throw TestSuiteParseFailed(
                    "Unable to open JSON suite file '" + filePath + "'"
                );
            }

            f >> data;
        }
        else {
            throw TestSuiteParseFailed(
                "Unsupported file format for '" + filePath +
                "'. Use .json"
            );
        }
    }
    catch (const nlohmann::json::parse_error& ex) {
        std::ostringstream oss;
        oss << "Invalid JSON in suite file " << filePath
            << ": " << ex.what()
            << " (byte " << ex.byte << ")";
        throw TestSuiteParseFailed(oss.str());
    }

    // --------------------------------------------------------------
    // Validate JSON against schema
    // --------------------------------------------------------------
   
    // Convert both schema and suite to jsoncons::json via dump/parse
    jsoncons::json schemaJson = ConvertFromNlohmann(suiteSchema_);
    jsoncons::json dataJson = ConvertFromNlohmann(data);

    // Build schema + validator (exactly like the docs)
    auto compiledSchema = jsoncons::jsonschema::make_schema(schemaJson);
    jsoncons::jsonschema::json_validator<jsoncons::json> validator(compiledSchema);

    try {
        validator.validate(dataJson);
    }
    catch (const std::exception& ex) {
        throw std::runtime_error(
            std::string("Suite validation error: ") + ex.what()
        );
    }

    // --------------------------------------------------------------
    // Apply normalisation logic
    // --------------------------------------------------------------
    return Normalise(data);
}

nlohmann::json SuiteParser::Normalise(nlohmann::json data) {
    return data;
}

jsoncons::json SuiteParser::ConvertFromNlohmann(const nlohmann::json& j)
{
    if (j.is_object()) {
        jsoncons::json result = jsoncons::json::object();
        for (auto& el : j.items()) {
            result[el.key()] = ConvertFromNlohmann(el.value());
        }
        return result;
    }
    else if (j.is_array()) {
        jsoncons::json result = jsoncons::json::array();
        for (auto& el : j) {
            result.push_back(ConvertFromNlohmann(el));
        }
        return result;
    }
    else if (j.is_string()) return j.get<std::string>();
    else if (j.is_boolean()) return j.get<bool>();
    else if (j.is_number_integer()) return j.get<long long>();
    else if (j.is_number_unsigned()) return j.get<unsigned long long>();
    else if (j.is_number_float()) return j.get<double>();
    else if (j.is_null()) return jsoncons::null_type();

    throw std::runtime_error("Unsupported JSON type");
}

}   // namespace Executor
}   // namespace WebWeaver
