from functools import wraps
import logging

from flask import request, abort
from flask import current_app


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):

        logging.debug(f"Checking for token in headers. Headers: \n{request.headers}")
        logging.debug(f"Request JSON contents: \n{request.json}")

        if "Authorization" in request.headers:
            token = request.headers["Authorization"].split(" ")[1]
            logging.info(f"Token found in headers: {token}")

        else:
            logging.debug("No token found in headers")
            return {
                "message": "Authentication Token is missing!",
                "data": None,
                "error": "Unauthorized",
            }, 401

        if not token == current_app.config["SECRET_KEY"]:
            logging.debug(
                f"Token found in headers, but is incorrect. Recieved: {token}"
            )
            return {
                "message": "Incorrect Authentication Token",
            }, 403

        return f(*args, **kwargs)

    return decorated
