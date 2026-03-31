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
import asyncio
import logging
import os
import typing
from quart import Quart
from webweaver.weavegate.apis import create_api_routes
from webweaver.weavegate.configuration_layout import CONFIGURATION_LAYOUT
from webweaver.weavegate.service_configuration import ServiceConfiguration
from webweaver.weavegate.service_state import ServiceState
from webweaver.weavegate.version import __version__ as gate_version

LOGGING_DATETIME_FORMAT_STRING = "%Y-%m-%d %H:%M:%S"
LOGGING_DEFAULT_LOG_LEVEL = logging.DEBUG
LOGGING_LOG_FORMAT_STRING = "%(asctime)s [%(levelname)s] %(message)s"


class WeaveGateService:
    """ WeaveGate service class. """
    __slots__ = ["_is_initialised", "_logger", "_quart_instance",
                 "_service_state", "_shutdown_complete", "_shutdown_event"]

    CONFIG_FILE_ENV: str = "WEBWEAVER_WEAVEGATE_CONFIG_FILE"
    CONFIG_REQUIRED_ENV: str = "WEBWEAVER_WEAVEGATE_CONFIG_FILE_REQUIRED"

    BOOL_TRUE_VALUES: set = {"1", "true", "yes", "on"}
    BOOL_FALSE_VALUES: set = {"0", "false", "no", "off"}

    def __init__(self, quart_instance: Quart):
        self._quart_instance = quart_instance

        self._is_initialised: bool = False
        self._logger: typing.Optional[logging.Logger] = None
        self._shutdown_event: asyncio.Event = asyncio.Event()
        self._shutdown_complete: asyncio.Event = asyncio.Event()

        self._logger: logging.Logger = logging.getLogger(__name__)
        log_format = logging.Formatter(LOGGING_LOG_FORMAT_STRING,
                                       LOGGING_DATETIME_FORMAT_STRING)
        console_stream = logging.StreamHandler()
        console_stream.setFormatter(log_format)
        self._logger.setLevel(LOGGING_DEFAULT_LOG_LEVEL)
        self._logger.addHandler(console_stream)

        self._service_state: ServiceState = ServiceState(version=gate_version)
        self._service_state.database_enabled = True

    @property
    def logger(self) -> logging.Logger:
        """
        Property getter for logger instance.

        returns:
            Returns the logger instance.
        """
        return self._logger

    @property
    def shutdown_event(self) -> asyncio.Event:
        """
        Event used to signal the shutdown of the service.

        This event should be awaited or checked by background tasks to
        gracefully stop operations when the application is shutting down.
        """
        return self._shutdown_event

    @property
    def shutdown_complete(self) -> asyncio.Event:
        """
        Event that indicates the service has completed its shutdown process.

        This should be set when all shutdown tasks and cleanup procedures have
        finished, allowing other components (like the main app) to know when
        it's safe to exit.
        """
        return self._shutdown_complete

    async def initialise(self) -> bool:
        """
        Microservice initialisation.  It should return a boolean
        (True => Successful, False => Unsuccessful), upon success
        self._is_initialised is set to True.

        Returns:
            Boolean: True => Successful, False => Unsuccessful.
        """
        if await self._initialise():
            self._is_initialised = True
            return True

        await self.stop()

        return False

    async def run(self) -> None:
        """
        Start the microservice.
        """

        if not self._is_initialised:
            self._logger.warning("Microservice is not initialised. Exiting run loop.")
            return

        self._logger.info("Microservice starting main loop.")

        try:
            while True:
                if self.shutdown_event.is_set():
                    break

                await self._main_loop()
                await asyncio.sleep(0.1)

        except KeyboardInterrupt:
            self._logger.debug("Service: Keyboard interrupt received.")
            self._shutdown_event.set()

        except asyncio.CancelledError:
            self._logger.debug("Service: Cancellation received.")
            raise

        finally:
            self._logger.info("Exiting microservice run loop...")
            await self.stop()
            self._logger.info("Shutdown complete.")

    async def stop(self) -> None:
        """
        Stop the microservice, it will wait until shutdown has been marked as
        completed before calling the shutdown method.
        """

        self._logger.info("Stopping microservice...")
        self._logger.info('Waiting for microservice shutdown to complete')

        self._shutdown_event.set()

        await self._shutdown()
        self._shutdown_complete.set()

        self._logger.info('Microservice shutdown complete...')

    async def _initialise(self) -> bool:
        """
        Microservice initialisation.  It should return a boolean
        (True => Successful, False => Unsuccessful).

        Returns:
            Boolean: True => Successful, False => Unsuccessful.
        """
        self._logger.info("WeaveGate Service %s", gate_version)
        self._logger.info(("Part of Webweaver "
                           "(https://github.com/SwatKat1977/WebWeaver)"))
        self._logger.info("Copyright 2025-2026 Webweaver Development Team")
        self._logger.info(("Licensed under the GNU General Public License, "
                           "Version 2.0"))

        if not self._manage_configuration():
            return False

        self._logger.info('Setting logging level to %s',
                          ServiceConfiguration().logging_log_level)
        self._logger.setLevel(ServiceConfiguration().logging_log_level)

        self._quart_instance.register_blueprint(
            create_api_routes(self._logger), url_prefix="")

        return True

    async def _main_loop(self) -> None:
        """ Method for main microservice loop. """

    async def _shutdown(self):
        """ Method for microservice shutdown. """

    def _check_for_configuration(self,
                                 config_file_env: str,
                                 config_file_required_env: str):
        """
        Check whether a configuration file is required and available based
        on environment variables.

        This function inspects two environment variables:
          - One specifying the path to a configuration file.
          - One specifying whether the configuration file is required.

        It validates the "required" flag against known boolean true/false
        values, determines whether the configuration file is missing when
        required, and returns the appropriate error status and state.

        Args:
            config_file_env (str):
                The name of the environment variable that holds the
                configuration file path.
            config_file_required_env (str):
                The name of the environment variable that indicates whether the
                configuration file is required.
                Expected values (case-insensitive):
                "true", "1", "yes", "on", "false", "0", "no", "off".

        Returns:
            tuple[str | None, bool, str | None]:
                A tuple containing:
                - `error_status` (str | None): An error message if a fatal
                  error occurred, otherwise None.
                - `config_file_required` (bool): Whether a configuration file
                  is required.
                - `config_file` (str | None): The configuration file path if
                  defined, otherwise None.

        Notes:
            - If `config_file_required_env` contains an invalid value, an error
              message is returned.
            - If a configuration file is required but not provided, an error
              message is returned.
            - If both checks pass, `error_status` will be None.

        Example:
            >>> os.environ["MY_CONFIG_FILE"] = "/etc/app.conf"
            >>> os.environ["MY_CONFIG_FILE_REQUIRED"] = "true"
            >>> self._check_for_configuration("MY_CONFIG_FILE",
                                              "MY_CONFIG_FILE_REQUIRED")
            (None, True, "/etc/app.conf")
        """
        # Default return values
        config_file_required: bool = False
        error_status: typing.Optional[str] = None

        config_file = os.getenv(config_file_env, None)
        raw_required = os.getenv(config_file_required_env,
                                 "false").strip().lower()

        # Check if it's a true value.
        if raw_required in self.BOOL_TRUE_VALUES:
            config_file_required = True

        # Check if it's a false value.
        elif raw_required in self.BOOL_FALSE_VALUES:
            config_file_required = False

        # Unknown value - e.g. not true or false value.
        else:
            error_status = (f"Invalid value for {config_file_required_env}: "
                            f"'{raw_required}'")

        if not error_status and not config_file and config_file_required:
            error_status = "Configuration file is not defined"

        return error_status, config_file_required, config_file

    def _manage_configuration(self) -> bool:
        """
        Manage the service configuration.
        """
        error_status, required, config_file = self._check_for_configuration(
            self.CONFIG_FILE_ENV,self.CONFIG_REQUIRED_ENV)
        if error_status:
            self._logger.critical(error_status)
            return False

        ServiceConfiguration().configure(CONFIGURATION_LAYOUT,
                                         config_file, required)

        try:
            ServiceConfiguration().process_config()

        except ValueError as ex:
            self._logger.critical("Configuration error : %s", str(ex))
            return False

        self._logger.info("Configuration")
        self._logger.info("=============")

        self._logger.info("Configuration file required: %s",
                          "True" if required else "False")
        self._logger.info("Configuration file : %s",
                          "None"if not required else config_file)
        self._logger.info("[logging]")
        self._logger.info("=> Log level : %s",
                          ServiceConfiguration().logging_log_level)
        self._logger.info("[database]")
        self._logger.info("=> Filename : %s",
                          ServiceConfiguration().database_filename)
        self._logger.info("=> Journal mode : %s",
                          ServiceConfiguration().database_journal_mode)
        self._logger.info("=> Busy timeout : %d",
                          ServiceConfiguration().database_busy_timeout)

        return True
