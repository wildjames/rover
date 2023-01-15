from functools import wraps
import logging

from flask import request, abort
from flask import current_app


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):

        if "Authorization" in request.headers:
            token = request.headers["Authorization"].split(" ")[1]

        else:
            logging.debug("No token found in headers")
            return {
                "message": "Authentication Token is missing!",
                "data": None,
                "error": "Unauthorized",
            }, 401

        if token != current_app.config["SECRET_KEY"]:
            logging.debug(
                f"Token found in headers, but is incorrect. Recieved: {token} | Expected: {current_app.config['SECRET_KEY']}"
            )
            return {
                "message": "Incorrect Authentication Token",
            }, 403

        return f(*args, **kwargs)

    return decorated
