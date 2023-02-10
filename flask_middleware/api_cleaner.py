import logging

logger = logging.getLogger(__name__)

from typing import Dict

import requests
from auth_middleware import token_required
from flask import Flask, render_template, request
from flask_cors import CORS
import os
import time


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
t0 = time.time()
contact = True
while time.time() - t0 < 30:
    try:
        # System configuration information gathering
        system_state = requests.get(
            controller_address_base.format("system_info")
        ).json()
        contact = True
        break
    except requests.exceptions.ConnectionError:
        logger.warning("Rover API server could not connect to controller.")
        contact = False

    time.sleep(1)

# Necessary variables
if contact:
    num_leds = system_state["led_data"]["num_leds"]
    num_relays = system_state["relay_data"]["num_relays"]
else:
    num_leds = 0
    num_relays = 0


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


@app.route("/config", methods=["POST"])
@token_required
def config():
    data = request.json

    logger.debug(f"Rover received configuration request: {data}")

    payload = {}

    if "sleep_time" in data.keys():
        value = data["sleep_time"]
        if value:
            try:
                value = float(value)
            except ValueError:
                logger.error(f"Sleep threshold value {value} is not a float.")
                return {"message": "failure: sleep_time value is not a float."}

            payload["sleep_time"] = value

    if "sleep_enable" in data.keys():
        value = data["sleep_enable"]
        if value != "" or value is not None:
            try:
                value = int(value)
            except ValueError:
                logger.error(f"Enable sleep value {value} is not an int.")
                return {"message": "failure: Enable sleep value is not an int."}

            if not (value == 0 or value == 1):
                logger.error(f"Enable sleep value {value} is not 0 or 1.")
                return {"message": "failure: Enable sleep value is not 0 or 1."}

            payload["sleep_enable"] = value

    logger.debug("Passing forward payload: {}".format(payload))

    response = requests.post(
        controller_address_base.format("config"), json=payload
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


@app.route("/relay_control", methods=["POST"])
@token_required
def relay_control():
    """Set the relay states to the defined states in the request JSON.

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
    logger.debug(f"Rover received relay command: {data}")

    if "states" not in data.keys():
        logger.error(f"relay command is invalid.")
        return {"message": "failure: No states in command JSON"}

    relay_command = data["states"]

    for pair in data["states"]:
        if not isinstance(pair, list):
            logger.error(f"relay command is invalid: {relay_command}")
            return {"message": "failure: Bad relay command"}

        if len(pair) != 2:
            logger.error(f"relay command is invalid: {relay_command}")
            return {"message": "failure: Bad relay command"}

        if pair[0] >= num_relays or pair[0] < 0:
            logger.error(f"relay index for {pair} is out of range.")
            return {"message": "failure: relay index out of range"}

        if pair[1] not in [0, 1]:
            logger.error(f"relay state for {pair} is invalid.")
            return {"message": "failure: Bad relay state"}

    response = requests.post(
        controller_address_base.format("relay_command"), json=relay_command
    ).json()

    return response


@app.route("/motor_command", methods=["POST"])
@token_required
def motor_command():
    logger.info("Recieved motor command")
    
    response = requests.post(
        controller_address_base.format("motor_command"), json=request.json
    ).json()

    return response


if __name__ == "__main__":
    logger.info("Starting server")
    app.run(host="0.0.0.0", port=8000, use_reloader=True, threaded=True, debug=True)
