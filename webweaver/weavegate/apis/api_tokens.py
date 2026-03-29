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
from webweaver.weavegate.apis.api_tokens_view import ApiTokensView


def create_blueprint(logger: logging.Logger) -> Blueprint:
    view = ApiTokensView(logger)

    blueprint = Blueprint('tokens_api', __name__)

    logger.debug("--------------- Registering tokens routes ---------------")

    logger.info(("=> /tokens/register [POST] : Register an access token to a "
                 "Studio install"))

    @blueprint.route("/register", methods=['POST'])
    async def register_token():
        return await view.register_token()

    return blueprint
