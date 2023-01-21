import logging
from typing import Dict

import requests
from auth_middleware import token_required
from flask import Flask, render_template, request
from flask_cors import CORS

logging.basicConfig(
    filename="/home/rover/log/rover_flask.log",
    filemode="a",
    format="[%(asctime)s] %(levelname)-8s    %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.DEBUG,
)
logging.info("Loading flask script")

controller_address_base = "http://localhost:8001/{}"

# Flask app setup
app = Flask(__name__)
CORS(app)

logging.info("Rover API server getting basic info.")
try:
    # # system configuration information gathering
    system_state = requests.get(controller_address_base.format("system_info")).json()
    contact = True
except requests.exceptions.ConnectionError:
    logging.warning("Rover API server could not connect to controller.")
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
            logging.info("Rover API server successfully contacted controller.")
        status_message = (
            "Contacted the backend successfully - hardware control is available."
        )
    except requests.exceptions.ConnectionError:
        logging.warning("Rover API server could not connect to controller.")
        status_message = (
            "Could not contact the backend! I don't have any hardware control."
        )

    return render_template("index.html", status_message=status_message)


@app.route("/system_info")
# @token_required
def system_info():
    """Returns a JSON object containing system information."""

    logging.debug(f"Rover received system info request. Headers: \n{request.headers}")

    system_state = requests.get(controller_address_base.format("system_info")).json()
    return system_state


@app.route("/led_control", methods=["POST"])
# @token_required
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
    logging.debug(f"Rover received LED command: {data}")

    if "states" not in data.keys():
        logging.error(f"LED command is invalid.")
        return {"message": "failure: No states in command JSON"}

    led_command = data["states"]

    for pair in data["states"]:
        if not isinstance(pair, list):
            logging.error(f"LED command is invalid: {led_command}")
            return {"message": "failure: Bad LED command"}

        if len(pair) != 2:
            logging.error(f"LED command is invalid: {led_command}")
            return {"message": "failure: Bad LED command"}

        if pair[0] >= num_leds or pair[0] < 0:
            logging.error(f"LED index for {pair} is out of range.")
            return {"message": "failure: LED index out of range"}

        if pair[1] not in [0, 1]:
            logging.error(f"LED state for {pair} is invalid.")
            return {"message": "failure: Bad LED state"}

    response = requests.post(
        controller_address_base.format("led_command"), json=led_command
    ).json()

    return response


@app.route("/motor_init", methods=["POST"])
def motor_init():
    """Initializes the motors."""
    response = requests.post(controller_address_base.format("motor_init")).json()
    return response


@app.route("/motor_arm", methods=["POST"])
def motor_arm():
    """Arms the motors."""
    response = requests.post(controller_address_base.format("motor_arm")).json()
    return response


@app.route("/motor_info", methods=["GET"])
def motor_info():
    """Returns a JSON object containing motor information."""
    response = requests.get(controller_address_base.format("motor_info")).json()
    return response


@app.route("/motor_command", methods=["POST"])
def motor_command():
    reponse = requests.post(
        controller_address_base.format("motor_command"), json=request.json
    ).json()
    return reponse


if __name__ == "__main__":
    logging.info("Starting server")
    app.run(host="0.0.0.0", port=8000, use_reloader=True, threaded=True, debug=True)
