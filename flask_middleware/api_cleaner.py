import logging

logger = logging.getLogger(__name__)

from typing import Dict

import requests
from auth_middleware import token_required
from flask import Flask, render_template, request
from flask_cors import CORS
import os


logger.info("Loading flask script")

controller_address_base = "http://localhost:8001/{}"

# If a token exists, use it. Otherwise, generate one.
token_location = os.path.join(os.path.dirname(__file__), "token.txt")
if os.path.exists(token_location):
    with open(token_location, "r") as f:
        token = f.read().strip()
else:
    import random

    chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890!@£$%^&*"
    token = "".join(random.choices(chars, k=32))
    with open(token_location, "w") as f:
        f.write(token)


# Flask app setup
app = Flask(__name__)
app.config["SECRET_KEY"] = token
CORS(app)


logger.info("Rover API server getting basic info.")
try:
    # # system configuration information gathering
    system_state = requests.get(controller_address_base.format("system_info")).json()
    contact = True
except requests.exceptions.ConnectionError:
    logger.warning("Rover API server could not connect to controller.")
    contact = False

# Necessary variables
if contact:
    num_leds = system_state["led_data"]["num_leds"]
else:
    num_leds = 0


@app.route("/")
def index():
    try:
        # # system configuration information gathering
        resp = requests.get(controller_address_base.format("ping")).json()
        if resp["message"] == "pong":
            logger.info("Rover API server successfully contacted controller.")
        status_message = (
            "Contacted the backend successfully - hardware control is available."
        )
    except requests.exceptions.ConnectionError:
        logger.warning("Rover API server could not connect to controller.")
        status_message = (
            "Could not contact the backend! I don't have any hardware control."
        )

    return render_template("index.html", status_message=status_message)


@app.route("/ping", methods=["GET"])
@token_required
def ping():
    logger.info("Received ping request")
    response = requests.get(controller_address_base.format("ping")).json()
    return response


@app.route("/system_info")
@token_required
def system_info():
    """Returns a JSON object containing system information."""

    logger.debug(f"Rover received system info request. Headers: \n{request.headers}")

    system_state = requests.get(controller_address_base.format("system_info")).json()
    return system_state


@app.route("/configure_inactivity", methods=["POST"])
@token_required
def configure_inactivity():
    data = request.json

    payload = {}

    if "timeout" in data.keys():
        payload["timeout"] = data["timeout"]
    if "enable_sleep" in data.keys():
        payload["enable_sleep"] = data["enable_sleep"]

    response = requests.post(
        controller_address_base.format("configure_inactivity"), json=payload
    ).json()

    return response
    


@app.route("/led_control", methods=["POST"])
@token_required
def led_control():
    """Set the LED states to the defined states in the request JSON.

    This passes the command on to the controller, but since the controller has to run as root I don't
    want to expose it to the internet. This checks the request for validity and sensibleness, then passes on
    only the command part of the request.

    Request JSON format:
    {
        "states": list of pairs, (index, state)
    }

    Response JSON format:
    {
        "message": "success" | "failure"
    }
    """
    data: Dict = request.json
    logger.debug(f"Rover received LED command: {data}")

    if "states" not in data.keys():
        logger.error(f"LED command is invalid.")
        return {"message": "failure: No states in command JSON"}

    led_command = data["states"]

    for pair in data["states"]:
        if not isinstance(pair, list):
            logger.error(f"LED command is invalid: {led_command}")
            return {"message": "failure: Bad LED command"}

        if len(pair) != 2:
            logger.error(f"LED command is invalid: {led_command}")
            return {"message": "failure: Bad LED command"}

        if pair[0] >= num_leds or pair[0] < 0:
            logger.error(f"LED index for {pair} is out of range.")
            return {"message": "failure: LED index out of range"}

        if pair[1] not in [0, 1]:
            logger.error(f"LED state for {pair} is invalid.")
            return {"message": "failure: Bad LED state"}

    response = requests.post(
        controller_address_base.format("led_command"), json=led_command
    ).json()

    return response


@app.route("/motor_init", methods=["POST"])
@token_required
def motor_init():
    """Initializes the motors."""
    response = requests.post(controller_address_base.format("motor_init")).json()
    return response


@app.route("/motor_close", methods=["POST"])
@token_required
def motor_close():
    """Closes the motors."""
    response = requests.post(controller_address_base.format("motor_close")).json()
    return response


@app.route("/motor_arm", methods=["POST"])
@token_required
def motor_arm():
    """Arms the motors."""
    response = requests.post(controller_address_base.format("motor_arm")).json()
    return response


@app.route("/motor_info", methods=["GET"])
@token_required
def motor_info():
    """Returns a JSON object containing motor information."""
    response = requests.get(controller_address_base.format("motor_info")).json()
    return response


@app.route("/motor_command", methods=["POST"])
@token_required
def motor_command():
    reponse = requests.post(
        controller_address_base.format("motor_command"), json=request.json
    ).json()
    return reponse


@app.route("/motor_stop", methods=["POST"])
@token_required
def motor_stop():
    response = requests.post(controller_address_base.format("motor_stop")).json()
    return response


@app.route("/motor_panic", methods=["POST"])
@token_required
def motor_panic():
    response = requests.post(controller_address_base.format("motor_panic")).json()
    return response


if __name__ == "__main__":
    logger.info("Starting server")
    app.run(host="0.0.0.0", port=8000, use_reloader=True, threaded=True, debug=True)
