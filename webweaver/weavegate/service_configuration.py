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
from configuration_layout import ConfigurationConstants as constants
from webweaver.weavegate.configuration_manager import ConfigurationManager
from webweaver.weavegate.thread_safe_singleton import ThreadSafeSingleton


class ServiceConfiguration(ConfigurationManager,
                           metaclass=ThreadSafeSingleton):
    """ Configuration accessor for Weavegate """

    @property
    def logging_log_level(self) -> str:
        """ Configuration property : Logging | log level """
        return str(ServiceConfiguration().get_entry(
            constants.SECTION_LOGGING, constants.LOGGING_LOG_LEVEL))

    @property
    def database_filename(self) -> str:
        """ Configuration property : Database | filename """
        return str(ServiceConfiguration().get_entry(
            constants.SECTION_DATABASE, constants.DATABASE_FILENAME))

    @property
    def database_journal_mode(self) -> str:
        """ Configuration property : Database | journal mode """
        return str(ServiceConfiguration().get_entry(
            constants.SECTION_DATABASE, constants.DATABASE_JOURNAL_MODE))

    @property
    def database_busy_timeout(self) -> int:
        """ Configuration property : Database | busy timeout """
        return int(ServiceConfiguration().get_entry(
            constants.SECTION_DATABASE, constants.DATABASE_BUSY_TIMEOUT))
