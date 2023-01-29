import logging
logger = logging.getLogger(__name__)

from functools import wraps

from flask import request, abort
from flask import current_app


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):

        if "Authorization" in request.headers:
            try:
                token = request.headers["Authorization"].split(" ")[1]
            except:
                return {
                    "message": "Authentication Token is missing!",
                    "data": None,
                    "error": "Unauthorized",
                }, 401

        else:
            logger.debug("No token found in headers")
            return {
                "message": "Authentication Token is missing!",
                "data": None,
                "error": "Unauthorized",
            }, 401

        if token != current_app.config["SECRET_KEY"]:
            logger.debug(
                f"Token found in headers, but is incorrect. Recieved: {token} | Expected: {current_app.config['SECRET_KEY']}"
            )
            return {
                "message": "Incorrect Authentication Token",
            }, 403

        return f(*args, **kwargs)

    return decorated
