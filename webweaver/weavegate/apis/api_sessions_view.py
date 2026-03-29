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

SCHEMA_START_SESSION_REQUEST: dict = {
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

SCHEMA_SESSION_HEARTBEAT_REQUEST: dict = {
    "$schema": "http://json-schema.org/draft-07/schema#",

    "type": "object",
    "additionalProperties": False,

    "properties":
        {
            "session_id":
                {
                    "type": "string"
                }
        },
    "required": ["session_id"]
}


class ApiSessionsView(BaseApiView):

    def __init__(self, logger: logging.Logger) -> None:
        self._logger = logger.getChild(__name__)

    @validate_json(SCHEMA_START_SESSION_REQUEST)
    async def start_session(self,
                            request_msg: ApiResponse) -> quart.Response:
        logging.info("(start_session) Token: %s", request_msg.body.token)

        response_body: dict = {
            "session_id": "PLACEHOLDER"
        }

        return quart.Response(json.dumps(response_body),
                              status=http.HTTPStatus.OK,
                              content_type="application/json")

    @validate_json(SCHEMA_SESSION_HEARTBEAT_REQUEST)
    async def session_heartbeat(self,
                                request_msg: ApiResponse) -> quart.Response:
        logging.info("(session_heartbeat) Session ID: %s",
                     request_msg.body.session_id)
        response_body: dict = {
            "status": True
        }

        return quart.Response(json.dumps(response_body),
                              status=http.HTTPStatus.OK,
                              content_type="application/json")
