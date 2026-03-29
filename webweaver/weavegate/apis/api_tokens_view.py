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

    def __init__(self, logger: logging.Logger) -> None:
        self._logger = logger.getChild(__name__)

    @validate_json(SCHEMA_REGISTER_TOKEN_REQUEST)
    async def register_token(self, request_msg: ApiResponse):
        token: str = request_msg.body.token
        self._logger.info("Token: %s", token)

        response_body: dict = {
            "status": True
        }

        return quart.Response(json.dumps(response_body),
                              status=http.HTTPStatus.OK,
                              content_type="application/json")
