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
import http
import json
import logging
import quart
from webweaver.weavegate.apis.base_api_view import (ApiResponse,
                                                    BaseApiView,
                                                    validate_json)

SCHEMA_REGISTER_TOKEN_REQUEST: dict = {
    "$schema": "http://json-schema.org/draft-07/schema#",

    "type": "object",
    "additionalProperties": False,

    "properties":
        {
            "token":
                {
                    "type": "string"
                }
        },
    "required": ["token"]
}


class ApiTokensView(BaseApiView):
    """View handling token-related API operations.

    This class contains handlers for endpoints related to access token
    management, such as registering tokens for a Studio installation.
    """

    def __init__(self, logger: logging.Logger) -> None:
        """Initialize the ApiTokensView.

        Args:
            logger (logging.Logger): Parent logger instance used to create
                a namespaced logger for this view.
        """
        self._logger = logger.getChild(__name__)

    @validate_json(SCHEMA_REGISTER_TOKEN_REQUEST)
    async def register_token(self, request_msg: ApiResponse):
        """Handle token registration requests.

        Validates the incoming JSON payload against
        SCHEMA_REGISTER_TOKEN_REQUEST and extracts the token value.
        Logs the token and returns a success response.

        Args:
            request_msg (ApiResponse): Parsed and validated request message
                containing the request body.

        Returns:
            quart.Response: JSON response indicating success.
        """
        token: str = request_msg.body.token
        self._logger.info("(register_token) Token: %s", token)

        response_body: dict = {
            "status": True
        }

        return quart.Response(json.dumps(response_body),
                              status=http.HTTPStatus.OK,
                              content_type="application/json")
