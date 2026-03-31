"""
This source file is part of Web Weaver
For the latest info, see https://github.com/SwatKat1977/WebWeaver

Copyright 2025-2026 SwatKat1977

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.
"""
from webweaver.weavegate import configuration_setup


class ConfigurationConstants:
    """ Constants for the microservice configuration. """
    # pylint: disable=too-few-public-methods

    SECTION_LOGGING: str = 'logging'
    SECTION_DATABASE: str = 'database'

    LOGGING_LOG_LEVEL: str = 'log_level'
    LOG_LEVEL_DEBUG: str = 'DEBUG'
    LOG_LEVEL_INFO: str = 'INFO'

    DATABASE_FILENAME: str = "filename"
    DATABASE_JOURNAL_MODE: str = "journal_mode"
    DATABASE_BUSY_TIMEOUT: str = "busy_timeout"


CONFIGURATION_LAYOUT = configuration_setup.ConfigurationSetup(
    {
        ConfigurationConstants.SECTION_LOGGING: [
            configuration_setup.ConfigurationSetupItem(
                ConfigurationConstants.LOGGING_LOG_LEVEL,
                configuration_setup.ConfigItemDataType.STRING,
                valid_values=[ConfigurationConstants.LOG_LEVEL_DEBUG,
                              ConfigurationConstants.LOG_LEVEL_INFO],
                default_value=ConfigurationConstants.LOG_LEVEL_INFO)
        ],
        ConfigurationConstants.SECTION_DATABASE: [
            configuration_setup.ConfigurationSetupItem(
                ConfigurationConstants.DATABASE_FILENAME,
                configuration_setup.ConfigItemDataType.STRING),
            configuration_setup.ConfigurationSetupItem(
                ConfigurationConstants.DATABASE_JOURNAL_MODE,
                configuration_setup.ConfigItemDataType.STRING,
                default_value="wal"),
            configuration_setup.ConfigurationSetupItem(
                ConfigurationConstants.DATABASE_BUSY_TIMEOUT,
                configuration_setup.ConfigItemDataType.INTEGER,
                default_value=5000),
        ],
    }
)
