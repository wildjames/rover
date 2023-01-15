from functools import wraps

from flask import request, abort
from flask import current_app


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if "Authorization" in request.headers:
            token = request.headers["Authorization"].split(" ")[1]

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
