import logging

logger = logging.getLogger(__name__)

logging.basicConfig(
    filename="/home/rover/rover/log/rover_controller.log",
    filemode="a",
    format="[%(asctime)s] %(levelname)-8s    %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.INFO,
)

from typing import Dict

import os

import relay_control
import led_control
import motor_control
import keep_alive_middleware
import environment_logger

from flask import Flask, request


# Flask app setup
app = Flask(__name__)

# Run the activity monitor if we are NOT in the main thread, if the reloader is enabled.
if not app.debug or os.environ.get("WERKZEUG_RUN_MAIN") == "true":
    keep_alive_middleware.check_inactivity()

    environment_logger.log_environment()
    environment_logger.upload_logs()


@app.route("/ping", methods=["GET"])
@keep_alive_middleware.keep_alive
def ping():
    """Returns a JSON with no useful information. Functions as a keepalive endpoint."""
    logger.info("Received ping request")
    return {"message": "pong"}


@app.route("/system_info", methods=["GET"])
@keep_alive_middleware.keep_alive
def system_info():
    """Returns a JSON object containing system information."""
    logger.info("Received a request for system information")

    info_dict = {
        "led_data": {
            "num_leds": len(led_control.leds),
            "led_states": led_control.get_led_state(),
        },
        "relay_data": {
            "num_relays": len(relay_control.relays),
            "relay_states": relay_control.get_relay_state(),
        },
        "motor_data": {
            "num_motors": len(motor_control.MOTOR_KEYS),
            "motor_actual_speeds": motor_control.motor_actual_speeds,
            "motor_target_speeds": motor_control.motor_target_speeds,
            "motor_throttles": motor_control.motor_throttles,
        },
        "sleep_data": {
            "sleep_time": keep_alive_middleware.SLEEP_THRESHOLD,
            "enable_sleep": int(keep_alive_middleware.ENABLE_SLEEP),
        },
        "environment_logger": {
            "log_interval": environment_logger.LOG_INTERVAL,
            "log_purge_interval": environment_logger.LOG_PURGE_INTERVAL,
            "upload_interval": environment_logger.UPLOAD_INTERVAL,
        },
    }

    logger.info("Returning system info: {}".format(info_dict))

    return info_dict


@app.route("/config", methods=["POST"])
@keep_alive_middleware.keep_alive
def config():
    """Sets configuration for internal variables.

    JSON payload can have:
    {
        "sleep_time": <int>,
        "sleep_enable": <bool>
    }

    both are optional.
    """
    global keep_alive_middleware

    logger.debug("Received configuration")
    logger.debug("Request data: {}".format(request.json))

    data = request.json

    if "sleep_time" in data:
        keep_alive_middleware.SLEEP_THRESHOLD = data["sleep_time"]
        logger.info(
            "Set inactivity timeout to {}".format(keep_alive_middleware.SLEEP_THRESHOLD)
        )

    if "sleep_enable" in data:
        logger.info("Received enable_sleep: {}".format(data["sleep_enable"]))
        keep_alive_middleware.ENABLE_SLEEP = bool(data["sleep_enable"])
        logger.info("Set enable_sleep to {}".format(keep_alive_middleware.ENABLE_SLEEP))

    return {"message": "success"}


@app.route("/motor_command", methods=["POST"])
@keep_alive_middleware.keep_alive
def motor_command():
    """Control motors.
    The JSON payload should contain dictionaries, with at least the key "command": <str>,
    followed by any other keys required for the command.
    Sometimes, this will also include a motor index, one of:
        fr: front right
        fl: front left
        br: back right
        bl: back left
    If a list of commands is sent, they will be executed in order.

    Returns a response message for each command, something like:
        {
            "command": str,
            "message": str,
        }

    Command options:

    - init_motors: Initialize the motors, using the set configuration.
        Structure:
        {
            "command": "init_motors",
        }

    - close_motors: Close the serial connection to the motor controller
        Structure:
        {
            "command": "close_motors",
        }

    - set_motor_throttle: Set the throttle for the motors.
        Structure:
        {
            "command": "set_speed",
            "payload": {
                "fr": <speed, cm/s>,
            },
        }
    """

    logger.info("Received motor control request")
    logger.debug("Request data: {}".format(request.json))

    data = request.json

    response = {"message": "success", "command_status": []}

    if isinstance(data, list):
        logger.info("Received list of commands")
        for command in data:
            logger.info("Executing command: {}".format(command))
            is_ok = motor_control.execute_command(command)
            response["command_status"].append(is_ok)

    elif isinstance(data, dict):
        logger.info("Received single command")
        is_ok = motor_control.execute_command(data)
        response["command_status"].append(is_ok)

    else:
        # I don't actually think this code is reachable, but just in case...
        logger.error("Invalid data type: {}".format(type(data)))
        return {"message": "failure: invalid data type"}

    return response


@app.route("/led_command", methods=["POST"])
@keep_alive_middleware.keep_alive
def led_command():
    req_obj = request.json

    logger.info("Received LED command pairs (index, state): {}".format(req_obj))

    for led, state in req_obj:
        if not led_control.set_led_state(led, state):
            return {"message": "failure: Controller could not set LED state"}

    return {"message": "success"}


@app.route("/relay_command", methods=["POST"])
@keep_alive_middleware.keep_alive
def relay_command():
    req_obj = request.json

    logger.info("Received relay command pairs (index, state): {}".format(req_obj))

    for relay, state in req_obj:
        if not relay_control.set_relay_state(relay, state):
            return {"message": "failure: Controller could not set relay state"}

    return {"message": "success"}


if __name__ in "__main__":
    app.run(host="localhost", port=8001, use_reloader=False, threaded=False, debug=True)
