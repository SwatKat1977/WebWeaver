import logging
import quart
from .api_tokens import create_blueprint as tokens_create


def create_api_routes(logger: logging.Logger) -> quart.Blueprint:
    apis_bp = quart.Blueprint("apis", __name__)

    # Tokens API routes
    apis_bp.register_blueprint(tokens_create(logger), url_prefix="/tokens")

    return apis_bp
