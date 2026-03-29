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
