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
#ifndef SUITEPARSER_H_
#define SUITEPARSER_H_
#include <string>
#include <jsoncons/json.hpp>
#include "nlohmann/json.hpp"

namespace WebWeaver { namespace Executor {

/**
 * @class SuiteParser
 * @brief Loads, validates, and normalises WebWeaver test suite definitions.
 *
 * The SuiteParser class is responsible for:
 *   - Loading a JSON test suite file.
 *   - Validating it against a JSON Schema definition.
 *   - Returning a normalised version of the suite configuration with
 *     defaults applied.
 *
 * A parsed test suite is returned as nlohmann::json after validation and
 * normalisation.
 */
class SuiteParser {
 public:
    /**
     * @brief Default number of threads used when a suite does not specify
     *        thread_count.
     */
    static constexpr int DEFAULT_SUITE_THREAD_COUNT = 10;

    /**
     * @brief Default number of threads for tests when not explicitly provided.
     */
    static constexpr int DEFAULT_TEST_THREAD_COUNT = 10;

    /**
     * @brief Construct a SuiteParser using a JSON Schema file.
     *
     * The schema file is loaded and parsed immediately. If the file does not
     * exist or is not valid JSON, an exception is thrown.
     *
     * @param schemaFile Path to the JSON Schema file describing valid suite structure.
     */
    explicit SuiteParser(const std::string& schemaFile);

    /**
     * @brief Load, validate, and normalise a WebWeaver test suite.
     *
     * The provided file is parsed (JSON), validated against the loaded schema,
     * and then passed through normalisation rules to ensure all required fields
     * and defaults are present.
     *
     * @param filePath Path to the suite file (JSON).
     * @return A validated and normalised test suite as nlohmann::json.
     * @throws std::runtime_error If the file does not exist, is invalid JSON,
     *         or fails schema validation.
     */
    nlohmann::json LoadSuite(const std::string& filePath);

 private:
     /**
      * @brief The loaded JSON Schema used to validate suite files.
      */
    nlohmann::json suiteSchema_;

    /**
     * @brief Apply WebWeaver normalisation rules to the parsed suite.
     *
     * This includes:
     *   - Applying default parallel modes.
     *   - Handling thread_count inheritance.
     *   - Merging class definitions.
     *   - Ensuring include/exclude method lists are deduplicated.
     *
     * @param data Raw parsed suite JSON.
     * @return Normalised suite JSON.
     */
    nlohmann::json Normalise(nlohmann::json data);

    /**
     * @brief Convert an nlohmann::json instance to jsoncons::json.
     *
     * Required because jsoncons is used for schema validation while
     * nlohmann::json is the internal representation.
     *
     * @param jsonInstance A nlohmann::json instance.
     * @return Equivalent jsoncons::json instance.
     */
    jsoncons::json ConvertFromNlohmann(const nlohmann::json& jsonInstance);
};

}   // namespace Executor
}   // namespace WebWeaver

#endif  // SUITEPARSER_H_
