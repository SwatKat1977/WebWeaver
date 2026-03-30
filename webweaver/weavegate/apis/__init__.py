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
import quart
from webweaver.weavegate.apis.api_sessions import create_blueprint \
    as sessions_create
from webweaver.weavegate.apis.api_tokens import create_blueprint \
    as tokens_create


def create_api_routes(logger: logging.Logger) -> quart.Blueprint:
    """Create and configure API routes as a Quart Blueprint.

    This function initializes the main API blueprint and registers
    sub-blueprints for different API components, such as token-related
    routes.

    Args:
        logger (logging.Logger): Logger instance used for logging within
            the registered API routes.

    Returns:
        quart.Blueprint: Configured Quart blueprint containing all API routes.
    """
    apis_bp = quart.Blueprint("apis", __name__)

    # Sessions API routes
    apis_bp.register_blueprint(sessions_create(logger), url_prefix="/sessions")

    # Tokens API routes
    apis_bp.register_blueprint(tokens_create(logger), url_prefix="/tokens")

    return apis_bp
