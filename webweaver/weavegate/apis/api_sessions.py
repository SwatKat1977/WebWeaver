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
import logging
from quart import Blueprint
from webweaver.weavegate.apis.api_sessions_view import ApiSessionsView


def create_blueprint(logger: logging.Logger) -> Blueprint:
    """Create and configure the sessions API blueprint.

    This function sets up the Flask/Quart blueprint responsible for handling
    session-related endpoints. It initializes the `ApiSessionsView` with the
    provided logger and registers all relevant routes for session management.

    Registered routes:
        - POST /sessions/start:
            Starts a new session with Weavegate.
        - POST /sessions/heartbeat:
            Sends a heartbeat to maintain an active session.

    Args:
        logger (logging.Logger): Logger instance used for route registration
            logging and passed to the underlying view.

    Returns:
        Blueprint: Configured blueprint containing all session-related routes.

    Notes:
        The route handlers delegate directly to methods on `ApiSessionsView`.
        These methods are expected to be asynchronous.
    """

    view = ApiSessionsView(logger)

    blueprint = Blueprint('sessions_api', __name__)

    logger.debug("--------------- Registering sessions routes ---------------")

    logger.info("=> /sessions/start [POST] : Start a new session to Weavegate")

    @blueprint.route("/start", methods=['POST'])
    async def start_session():
        # pylint: disable=no-value-for-parameter
        return await view.start_session()

    logger.info("=> /sessions/heartbeat [POST] : Send a session heartbeat")

    @blueprint.route("/heartbeat", methods=['POST'])
    async def session_heartbeat():
        # pylint: disable=no-value-for-parameter
        return await view.session_heartbeat()

    return blueprint
