// SPDX-License-Identifier: GPL-3.0-or-later
// WebWeaver — Copyright (c) 2025 SwatKat1977
// https://github.com/SwatKat1977/WebWeaver
#include <filesystem>                                   // NOLINT(build/c++17)
#include <fstream>
#include <map>
#include <set>
#include <string>
#include <utility>
#include <vector>
#include <jsoncons/json.hpp>
#include <jsoncons_ext/jsonschema/jsonschema.hpp>
#include "SuiteParser.h"
#include "WebWeaverExceptions.h"

namespace WebWeaver { namespace Executor {

SuiteParser::SuiteParser(const std::string& schemaFile) {
    // Try to open the file
    std::ifstream file(schemaFile);
    if (!file.is_open()) {
        throw TestSuiteSchemaFileNotFound(
            "Suite schema file '" + schemaFile + "' not found.");
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
            "Suite file '" + filePath + "' not found.");
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
                    "Unable to open JSON suite file '" + filePath + "'");
            }

            f >> data;
        } else {
            throw TestSuiteParseFailed(
                "Unsupported file format for '" + filePath +
                "'. Use .json");
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
    auto builtSchema = jsoncons::jsonschema::make_schema(schemaJson);
    jsoncons::jsonschema::json_validator<jsoncons::json> validator(builtSchema);

    try {
        validator.validate(dataJson);
    }
    catch (const std::exception& ex) {
        throw std::runtime_error(
            std::string("Suite validation error: ") + ex.what());
    }

    // --------------------------------------------------------------
    // Apply normalisation logic
    // --------------------------------------------------------------
    return Normalise(data);
}

nlohmann::json SuiteParser::Normalise(nlohmann::json data) {
    auto& suite = data["suite"];

    // Suite-level defaults
    if (!suite.contains("parallel")) {
        suite["parallel"] = "none";
    }

    if (!suite.contains("thread_count")) {
        suite["thread_count"] = DEFAULT_SUITE_THREAD_COUNT;
    }

    for (auto& test : data["tests"]) {
        // parallel inherits from suite if missing
        if (!test.contains("parallel"))
            test["parallel"] = suite["parallel"];

        // Compute thread_count
        if (test["parallel"] == "none") {
            // Default to 1 only if user did not specify
            if (!test.contains("thread_count"))
                test["thread_count"] = 1;
        } else {
            if (!test.contains("thread_count")) {
                if (suite.contains("thread_count")) {
                    test["thread_count"] = suite["thread_count"];
                } else {
                    test["thread_count"] = DEFAULT_TEST_THREAD_COUNT;
                }
            }
        }

        // ---------- Merge classes by name ----------

        std::map<std::string, nlohmann::json> merged;
        std::vector<std::string> order;

        for (auto& cls : test["classes"]) {
            std::string name;
            nlohmann::json methods;

            if (cls.is_string()) {
                name = cls.get<std::string>();
                methods = { {"include", nlohmann::json::array()},
                            {"exclude", nlohmann::json::array()} };
            } else {
                name = cls["name"];

                auto include = cls.value("methods", nlohmann::json::object())
                    .value("include", nlohmann::json::array());
                auto exclude = cls.value("methods", nlohmann::json::object())
                    .value("exclude", nlohmann::json::array());

                // Convert string → list
                if (include.is_string()) {
                    include = nlohmann::json::array({ include });
                }

                if (exclude.is_string()) {
                    exclude = nlohmann::json::array({ exclude });
                }

                methods = {
                    {"include", include},
                    {"exclude", exclude}
                };
            }

            // First encounter of this class
            if (merged.find(name) == merged.end()) {
                merged[name] = {
                    {"name", name},
                    {"methods", {
                        {"include", nlohmann::json::array()},
                        {"exclude", nlohmann::json::array()}
                    }}
                };
                order.push_back(name);
            }

            // Merge include/exclude with dedupe
            auto& dstInclude = merged[name]["methods"]["include"];
            auto& dstExclude = merged[name]["methods"]["exclude"];

            auto extend_unique = [](nlohmann::json& dst,
                                    const nlohmann::json& src) {
                    std::set<std::string> seen;
                    for (const auto& s : dst) {
                        seen.insert(s.get<std::string>());
                    }

                    for (const auto& s : src) {
                        std::string str = s.get<std::string>();
                        if (!seen.count(str)) {
                            dst.push_back(str);
                            seen.insert(str);
                        }
                    }
                };

            extend_unique(dstInclude, methods["include"]);
            extend_unique(dstExclude, methods["exclude"]);
        }

        // Rebuild classes in order
        nlohmann::json newClasses = nlohmann::json::array();
        for (const auto& name : order) {
            newClasses.push_back(merged[name]);
        }

        test["classes"] = std::move(newClasses);
    }

    return data;
}

jsoncons::json SuiteParser::ConvertFromNlohmann(
    const nlohmann::json& jsonInstance) {
    if (jsonInstance.is_object()) {
        jsoncons::json result = jsoncons::json::object();
        for (auto& el : jsonInstance.items()) {
            result[el.key()] = ConvertFromNlohmann(el.value());
        }

        return result;
    } else if (jsonInstance.is_array()) {
        jsoncons::json result = jsoncons::json::array();
        for (auto& element : jsonInstance) {
            result.push_back(ConvertFromNlohmann(element));
        }

        return result;
    } else if (jsonInstance.is_string()) {
        return jsonInstance.get<std::string>();
    } else if (jsonInstance.is_boolean()) {
        return jsonInstance.get<bool>();
    } else if (jsonInstance.is_number_integer()) {
        return jsonInstance.get<int64_t>();
    } else if (jsonInstance.is_number_unsigned()) {
        return jsonInstance.get<uint64_t>();
    } else if (jsonInstance.is_number_float()) {
        return jsonInstance.get<double>();
    } else if (jsonInstance.is_null()) {
        return jsoncons::null_type();
    }

    throw std::runtime_error("Unsupported JSON type");
}

}   // namespace Executor
}   // namespace WebWeaver
