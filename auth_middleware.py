from functools import wraps
import logging

from flask import request, abort
from flask import current_app


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        logging.debug(f"Checking for token in headers. Headers: {request.headers}")

        if "Authorization" in request.headers:
            token = request.headers["Authorization"].split(" ")[1]
            logging.info(f"Token found in headers: {token}")
            abort(401, "Authentication Token is missing!")
        
        if not token:
            return {
                "message": "Authentication Token is missing!",
                "data": None,
                "error": "Unauthorized",
            }, 401

        if not token == current_app.config["SECRET_KEY"]:
            return {
                "message": "Incorrect Authentication Token",
            }, 403

        return f(*args, **kwargs)

    return decorated
