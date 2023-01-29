import logging
from typing import List

import os

import led_control
import motor_control
from keep_alive_middleware import keep_alive, check_inactivity

from flask import Flask, request


logging.basicConfig(
    # filename="/home/rover/log/rover_controller.log",
    # filemode="a",
    format="[%(asctime)s] %(levelname)-8s    %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.DEBUG,
)


# Flask app setup
app = Flask(__name__)

# Run the activity monitor if we are NOT in the main thread, if the reloader is enabled.
if not app.debug or os.environ.get("WERKZEUG_RUN_MAIN") == "true":
    check_inactivity()

# Motor setup
ESC_pins = [12]
motors: List[motor_control.ESCController] = [
    motor_control.ESCController(pin, start_now=False) for pin in ESC_pins
]


@app.route("/ping", methods=["GET"])
@keep_alive
def ping():
    """Returns a JSON object containing a message."""
    logging.info("Received ping request")
    return {"message": "pong"}


@app.route("/system_info", methods=["GET"])
@keep_alive
def system_info():
    """Returns a JSON object containing system information."""

    info_dict = {
        "led_data": {
            "num_leds": len(led_control.leds),
            "led_states": led_control.get_led_state(),
        },
        "motor_data": {
            "num_motors": len(motors),
            "motor_states": [],
        },
    }

    # Gather motor data
    payload = []
    for m in motors:
        payload.append(
            {
                "pin": m.pin,
                "min_pulse": m.min_pulse_width,
                "max_pulse": m.max_pulse_width,
                "throttle": m.throttle,
                "started": m.started,
            }
        )

    info_dict["motor_data"]["motor_states"]= payload

    logging.info("Returning system info: {}".format(info_dict))

    return info_dict


@app.route("/motor_init", methods=["POST"])
@keep_alive
def motor_init():
    global motors

    logging.info("Initializing ESCs")
    try:
        for esc in motors:
            # Create an ESC object to control the ESC on pin 18.
            esc.init()

    except Exception as e:
        logging.exception("Failed to initialize ESCs")
        return {"message": f"failure: {e}"}

    return {"message": "success"}


@app.route("/motor_close", methods=["POST"])
@keep_alive
def motor_close():
    global motors

    for m in motors:
        logging.info("Closing ESC on pin {}".format(m.pwm.pin))
        m.close()

    return {"message": "success"}


@app.route("/motor_arm", methods=["POST"])
@keep_alive
def motor_arm():
    global motors

    for m in motors:
        logging.info("Controller is arming ESC on pin {}".format(m.pwm.pin))
        m.arm()
        logging.info("Done")

    return {"message": "success"}


@app.route("/motor_calibrate", methods=["POST"])
@keep_alive
def motor_calibrate():
    global motors

    req_obj = request.json
    to_calibrate = req_obj["target"]

    logging.info("Received motor calibration for index: {}".format(req_obj))

    for index in to_calibrate:
        if not motors[index]:
            return {"message": "failure: Motor index {} does not exist".format(index)}

    for index in to_calibrate:
        logging.info("Calibrating motor at index {}".format(index))
        m = motors[index]
        logging.info("Motor is on pin {}".format(m.pwm.pin))
        m.calibrate()

    return {"message": "success"}


@app.route("/motor_command", methods=["POST"])
@keep_alive
def motor_command():
    """Expects a JSON object containing a list of motor index and state pairs,
    keyed under "targets"
    """
    global motors

    req_obj = request.json
    command = req_obj["targets"]

    logging.info("Received motor command pairs (index, state): {}".format(command))

    for index, state in command:
        if not motors[index]:
            return {"message": "failure: Motor index {} does not exist".format(index)}

        if state < 0.0 or state > 1.0:
            return {"message": "failure: motor state must be between 0.0 and 1.0"}

    try:
        for index, state in command:
            motors[index].set_speed(state)
    except:
        logging.exception("Failed to set motor speed")
        return {"message": "failure: Controller could not set motor speed"}

    return {"message": "success"}


@app.route("/motor_stop", methods=["POST"])
@keep_alive
def motor_stop():
    global motors

    for m in motors:
        m.stop()

    return {"message": "success"}


@app.route("/motor_panic", methods=["POST"])
@keep_alive
def motor_panic():
    global motors

    for m in motors:
        m.estop()

    return {"message": "success"}


@app.route("/led_command", methods=["POST"])
@keep_alive
def led_command():
    req_obj = request.json

    logging.info("Received LED command pairs (index, state): {}".format(req_obj))

    for led, state in req_obj:
        if not led_control.set_led_state(led, state):
            return {"message": "failure: Controller could not set LED state"}

    return {"message": "success"}


if __name__ in "__main__":
    app.run(host="localhost", port=8001, use_reloader=False, threaded=True, debug=True)
